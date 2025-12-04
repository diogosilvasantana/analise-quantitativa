import redis.asyncio as redis
import json
import logging
from typing import Optional
from src.config import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD, REDIS_TTL

logger = logging.getLogger(__name__)

class RedisManager:
    def __init__(self, host: str = REDIS_HOST, port: int = REDIS_PORT, db: int = REDIS_DB, password: Optional[str] = REDIS_PASSWORD, ttl: int = REDIS_TTL):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.ttl = ttl
        self.redis = None
    
    async def connect(self):
        """Conecta ao Redis"""
        try:
            self.redis = await redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=True
            )
            await self.redis.ping()
            logger.info(f"✅ Conectado ao Redis em {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"❌ Erro ao conectar Redis em {self.host}:{self.port}: {e}")
            self.redis = None # Garante que o objeto redis é None em caso de falha
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None):
        """Salva valor em cache"""
        if not self.redis:
            logger.warning("⚠️ Redis não conectado. Não foi possível salvar em cache.")
            return
        try:
            await self.redis.setex(key, ttl if ttl is not None else self.ttl, value)
            logger.debug(f"✅ Cache set: {key}")
        except Exception as e:
            logger.error(f"❌ Erro ao set cache para {key}: {e}")
    
    async def get(self, key: str) -> Optional[str]:
        """Recupera valor do cache"""
        if not self.redis:
            logger.warning("⚠️ Redis não conectado. Não foi possível recuperar do cache.")
            return None
        try:
            value = await self.redis.get(key)
            logger.debug(f"✅ Cache get: {key}")
            return value
        except Exception as e:
            logger.error(f"❌ Erro ao get cache para {key}: {e}")
            return None
    
    async def disconnect(self):
        """Desconecta do Redis"""
        if self.redis:
            await self.redis.close()
            logger.info("Redis desconectado")
            self.redis = None
