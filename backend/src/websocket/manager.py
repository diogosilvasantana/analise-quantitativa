import logging
from typing import Set, List
from fastapi import WebSocket
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"✅ WebSocket conectado. Conexões ativas: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"❌ WebSocket desconectado. Conexões ativas: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Envia mensagem para todos os clientes conectados"""
        if not self.active_connections:
            logger.warning("⚠️ Nenhuma conexão ativa para broadcast.")
            return
        
        disconnected = set()
        
        for connection in list(self.active_connections): # Usar list() para evitar RuntimeError durante iteração e modificação
            try:
                await connection.send_json({
                    "type": "DASHBOARD_UPDATE", # Tipo de mensagem genérico para o dashboard
                    "data": message,
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f"❌ Erro ao enviar para cliente {connection.client}: {e}")
                disconnected.add(connection)
        
        # Remove conexões quebradas
        for connection in disconnected:
            self.disconnect(connection)
