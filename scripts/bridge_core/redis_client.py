import redis
import logging
import json
from .config import BridgeConfig

logger = logging.getLogger("Bridge.Redis")

class RedisClient:
    def __init__(self):
        self.client = None
        self.connect()

    def connect(self):
        try:
            self.client = redis.Redis(
                host=BridgeConfig.REDIS_HOST,
                port=BridgeConfig.REDIS_PORT,
                db=0,
                decode_responses=True
            )
            self.client.ping()
            logger.info(f"✅ Conectado ao Redis em {BridgeConfig.REDIS_HOST}:{BridgeConfig.REDIS_PORT}")
        except Exception as e:
            logger.error(f"❌ Falha ao conectar no Redis: {e}")
            self.client = None

    def publish(self, key: str, data: dict):
        if not self.client:
            return
        try:
            self.client.set(key, json.dumps(data))
        except Exception as e:
            logger.error(f"❌ Erro ao publicar no Redis: {e}")
