import asyncio
import logging
from src.websocket.manager import ConnectionManager
from src.indices.collector import IndicesCollector
from src.config import WS_UPDATE_INTERVAL

logger = logging.getLogger(__name__)

class WebSocketBroadcaster:
    def __init__(self, manager: ConnectionManager, collector: IndicesCollector, interval: float = WS_UPDATE_INTERVAL):
        self.manager = manager
        self.collector = collector
        self.interval = interval
        self.running = False
        self.broadcast_task: asyncio.Task = None
    
    async def start(self):
        """Inicia o broadcast periódico"""
        self.running = True
        logger.info(f"🔄 Iniciando broadcaster com intervalo de {self.interval}s")
        
        while self.running:
            try:
                # Coleta dados
                dashboard_data = await self.collector.collect_all()
                
                # Envia via WebSocket
                await self.manager.broadcast(dashboard_data.model_dump())
                
                # Aguarda intervalo
                await asyncio.sleep(self.interval)
            
            except asyncio.CancelledError:
                logger.info("⛔ Broadcaster task cancelada.")
                break
            except Exception as e:
                logger.error(f"❌ Erro no broadcaster: {e}")
                await asyncio.sleep(self.interval) # Espera antes de tentar novamente
    
    def stop(self):
        """Para o broadcaster"""
        self.running = False
        if self.broadcast_task:
            self.broadcast_task.cancel()
        logger.info("⛔ Broadcaster parado")
