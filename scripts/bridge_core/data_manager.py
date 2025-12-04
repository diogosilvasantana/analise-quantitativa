import threading
import time
import json
import datetime
import logging
from .config import BridgeConfig
from .mt5_client import MT5Client
from .investing_client import InvestingClient
from .calendar_client import CalendarClient
from .redis_client import RedisClient

logger = logging.getLogger("Bridge.DataManager")

class DataManager:
    def __init__(self):
        self.running = True
        self.mt5_client = MT5Client()
        self.investing_client = InvestingClient()
        self.calendar_client = CalendarClient()
        self.redis_client = RedisClient()
        
        # Cache
        self.macro_cache = {}
        self.calendar_cache = []
        self.cache_lock = threading.Lock()
        
        # Initialize Cache
        for name in BridgeConfig.MACRO_TARGETS:
            self.macro_cache[name] = {"valor": 0.0, "var": 0.0, "var_pct": 0.0}

        # Start Background Threads
        self.scrape_thread = threading.Thread(target=self._scrape_loop, daemon=True)
        self.scrape_thread.start()
        
        self.calendar_thread = threading.Thread(target=self._calendar_loop, daemon=True)
        self.calendar_thread.start()
        
        logger.info("🚀 Bridge Iniciado. Coletando dados...")

    def _calendar_loop(self):
        """
        Background loop to fetch Economic Calendar (Smart Polling).
        Checks every 1 minute, but only scrapes if necessary.
        """
        while self.running:
            # logger.debug("📅 Verificando necessidade de atualização do calendário...")
            
            # Pass current cache to client for decision making
            with self.cache_lock:
                current_cache = self.calendar_cache.copy()
            
            events = self.calendar_client.fetch_events(current_cache)
            
            if events:
                with self.cache_lock:
                    self.calendar_cache = events
            
            # Sleep for 1 minute (60s)
            for _ in range(60):
                if not self.running: break
                time.sleep(1)

    def _scrape_loop(self):
        """
        Background loop to fetch Macro Data via Scraping.
        """
        while self.running:
            logger.info("🔄 Iniciando ciclo de Scraping...")
            try:
                for name, url in BridgeConfig.MACRO_TARGETS.items():
                    data = self.investing_client.scrape_ticker(name, url)
                    
                    if data:
                        with self.cache_lock:
                            self.macro_cache[name] = data
            except Exception as e:
                logger.error(f"❌ Erro no loop de scraping: {e}")
            
            logger.info(f"⏳ Aguardando {BridgeConfig.SLOW_INTERVAL}s...")
            time.sleep(BridgeConfig.SLOW_INTERVAL)

    def run(self):
        """
        Main loop: Aggregates data and pushes to Redis.
        """
        try:
            while self.running:
                # 1. Get Fast Data (MT5)
                mt5_data = self.mt5_client.fetch_data()
                
                # 2. Get Slow Data (Scraping Cache)
                with self.cache_lock:
                    macro_data = self.macro_cache.copy()
                    calendar_data = self.calendar_cache.copy()
                
                # 3. Aggregate
                aggregated_data = {
                    "mt5": mt5_data,
                    "macro": macro_data,
                    "calendar": calendar_data,
                    "timestamp": datetime.datetime.now().isoformat()
                }
                
                # 4. Push to Redis
                self.redis_client.publish("market_data", aggregated_data)
                
                time.sleep(BridgeConfig.FAST_INTERVAL)
                
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        logger.info("🛑 Parando Bridge...")
        self.running = False
        self.mt5_client.shutdown()
