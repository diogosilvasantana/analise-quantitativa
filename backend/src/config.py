import os
from dotenv import load_dotenv

load_dotenv()

# API Settings
API_TITLE = "AI-TRADER-PRO Backend v1.0.0"
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Redis
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_TTL = int(os.getenv("REDIS_TTL", 300))  # 5 minutos

# Scraping
SCRAPING_DELAY_MIN = float(os.getenv("SCRAPING_DELAY_MIN", 0.5))
SCRAPING_DELAY_MAX = float(os.getenv("SCRAPING_DELAY_MAX", 2.0))
SCRAPING_TIMEOUT = int(os.getenv("SCRAPING_TIMEOUT", 10))
SCRAPING_RETRIES = int(os.getenv("SCRAPING_RETRIES", 3))

# MetaTrader5
MT5_HOST = os.getenv("MT5_HOST", "localhost")
MT5_PORT = int(os.getenv("MT5_PORT", 50000))
MT5_DI_SYMBOL = os.getenv("MT5_DI_SYMBOL", "WINZ25") # Símbolo para o DI

# WebSocket
WS_UPDATE_INTERVAL = float(os.getenv("WS_UPDATE_INTERVAL", 5.0))  # 5 segundos

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
