import asyncio
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import json
from datetime import datetime

from src.config import API_TITLE, API_HOST, API_PORT, DEBUG, WS_UPDATE_INTERVAL, MT5_HOST, MT5_PORT, MT5_DI_SYMBOL
from src.utils.logging_config import setup_logging
from src.indices.collector import IndicesCollector
from src.cache.redis_manager import RedisManager
from src.websocket.manager import ConnectionManager
from src.websocket.broadcaster import WebSocketBroadcaster

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Globals
redis_manager: RedisManager = None
indices_collector: IndicesCollector = None
connection_manager: ConnectionManager = ConnectionManager()
broadcaster: WebSocketBroadcaster = None
broadcaster_task: asyncio.Task = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"🚀 {API_TITLE} iniciando...")
    
    global redis_manager, indices_collector, broadcaster, broadcaster_task
    
    redis_manager = RedisManager()
    await redis_manager.connect()
    
    indices_collector = IndicesCollector(redis_manager)
    
    broadcaster = WebSocketBroadcaster(connection_manager, indices_collector, interval=WS_UPDATE_INTERVAL)
    broadcaster_task = asyncio.create_task(broadcaster.start())
    
    logger.info(f"✅ {API_TITLE} pronto!")
    
    yield
    
    # Shutdown
    logger.info("🛑 Encerrando...")
    broadcaster.stop()
    if broadcaster_task:
        await broadcaster_task # Espera a tarefa ser cancelada
    await redis_manager.disconnect()
    logger.info("✅ Encerrado")

app = FastAPI(title=API_TITLE, lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permite todas as origens para desenvolvimento
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/dashboard_data")
async def get_dashboard_data():
    """Retorna dados do dashboard (índices, commodities, taxas)"""
    try:
        data = await redis_manager.get("dashboard_data")
        if data:
            return json.loads(data)
        
        # Se não houver cache, coleta agora
        dashboard_data = await indices_collector.collect_all()
        return dashboard_data.model_dump()
    
    except Exception as e:
        logger.error(f"❌ Erro em /api/dashboard_data: {e}")
        return {"error": str(e)}

@app.websocket("/ws/dashboard")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket para receber dados do dashboard em tempo real"""
    try:
        await connection_manager.connect(websocket)
        
        # Envia o último estado do dashboard imediatamente após a conexão
        cached_data = await redis_manager.get("dashboard_data")
        if cached_data:
            await websocket.send_json({
                "type": "DASHBOARD_UPDATE",
                "data": json.loads(cached_data),
                "timestamp": datetime.now().isoformat()
            })
        
        while True:
            # Mantém conexão aberta, pode receber mensagens do cliente se necessário
            # Por enquanto, apenas espera para manter a conexão viva
            await websocket.receive_text() 
    
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
        logger.info("WebSocket desconectado")
    
    except Exception as e:
        logger.error(f"❌ Erro em WebSocket: {e}")
        connection_manager.disconnect(websocket)

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "ok", "app": API_TITLE}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=API_HOST, port=API_PORT, debug=DEBUG)
