import asyncio
import logging
import datetime
import aiohttp
import random
from .config import BridgeConfig
from .mt5_client import MT5Client
from .investing_client import InvestingClient
from .calendar_client import CalendarClient
from .redis_client import RedisClient

logger = logging.getLogger("Bridge.DataEngine")

class DataEngine:
    def __init__(self):
        self.running = True
        
        # Clients
        self.mt5 = MT5Client()
        self.investing = InvestingClient()
        self.calendar = CalendarClient()
        self.redis = RedisClient()
        
        # State/Cache
        self.macro_cache = {}
        self.calendar_cache = []
        self.tv_cache = {} 
        self.missing_in_mt5 = set() 
        
        # Initialize Macro Cache
        for name in BridgeConfig.MACRO_TARGETS:
            self.macro_cache[name] = {"valor": 0.0, "var": 0.0, "var_pct": 0.0}

    async def _fetch_macro_loop(self):
        """
        Async loop for Investing.com Scraper (Indices/Commodities).
        """
        async with aiohttp.ClientSession() as session:
            while self.running:
                logger.info("🔄 Scraping Macro Data...")
                tasks = []
                for name, url in BridgeConfig.MACRO_TARGETS.items():
                    tasks.append(self.investing.scrape_ticker(session, name, url))
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for i, name in enumerate(BridgeConfig.MACRO_TARGETS.keys()):
                    result = results[i]
                    if isinstance(result, dict):
                        self.macro_cache[name] = result
                
                # Jitter (300s + random 10-30s)
                sleep_time = BridgeConfig.SLOW_INTERVAL + random.randint(10, 30)
                await asyncio.sleep(sleep_time)

    async def _fetch_calendar_loop(self):
        """
        Async loop for Economic Calendar (Smart Polling).
        """
        async with aiohttp.ClientSession() as session:
            while self.running:
                # Pass copy of cache for decision making
                current_cache = self.calendar_cache.copy()
                
                events = await self.calendar.fetch_events(session, current_cache)
                if events:
                    self.calendar_cache = events
                
                # Check every minute
                # Jitter (60s + random 5-15s)
                sleep_time = 60 + random.randint(5, 15)
                await asyncio.sleep(sleep_time)

    async def _fetch_global_loop(self):
        """
        Loop for Global Data (Indices/Commodities) + Fallback.
        Replaces TVClient with Investing Scraper.
        """
        # Global Assets URLs (Investing.com)
        global_urls = {
            "SP500": "https://www.investing.com/indices/us-spx-500",
            "NASDAQ": "https://www.investing.com/indices/nq-100",
            "DXY": "https://www.investing.com/indices/usdollar",
            "VIX": "https://www.investing.com/indices/volatility-s-p-500",
            "US10Y": "https://www.investing.com/rates-bonds/u.s.-10-year-bond-yield",
            "BRENT": "https://www.investing.com/commodities/brent-oil",
            "GOLD": "https://www.investing.com/commodities/gold"
        }
        
        # Fallback URLs (Investing.com)
        fallback_urls = {
            "LREN3": "https://br.investing.com/equities/lojas-renner-on",
            "AXIA3": "https://br.investing.com/equities/centrais-eletricas-brasileiras-sa",
            "BBAS3": "https://br.investing.com/equities/banco-do-brasil-on",
            "RENT3": "https://br.investing.com/equities/localiza-rent-a-car-sa-on",
            "SBSP3": "https://br.investing.com/equities/sabesp-on",
            "VALE3": "https://br.investing.com/equities/vale-on",
            "PETR4": "https://br.investing.com/equities/petrobras-pn",
            "ITUB4": "https://br.investing.com/equities/itauunibanco-pn",
            "BBDC4": "https://br.investing.com/equities/bradesco-pn",
            "WEGE3": "https://br.investing.com/equities/weg-on",
            "BPAC11": "https://br.investing.com/equities/btgpactual-unit"
        }

        async with aiohttp.ClientSession() as session:
            while self.running:
                logger.info("🌍 Scraping Global Data...")
                
                # 1. Fetch Global Assets
                tasks = []
                names = []
                for name, url in global_urls.items():
                    names.append(name)
                    tasks.append(self.investing.scrape_ticker(session, name, url))
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for i, name in enumerate(names):
                    res = results[i]
                    if isinstance(res, dict):
                        # Format for Frontend (TV cache compatibility)
                        self.tv_cache[name] = {
                            "symbol": name,
                            "price": res["valor"],
                            "change": res["var"],
                            "change_pct": res["var_pct"]
                        }
                
                # 2. Fetch Fallback Assets (Investing Scraper)
                if self.missing_in_mt5:
                    logger.info(f"⚠️ Fallback (Scraper) ativado para: {self.missing_in_mt5}")
                    for symbol in self.missing_in_mt5:
                        if symbol in fallback_urls:
                            try:
                                url = fallback_urls[symbol]
                                data = await self.investing.scrape_ticker(session, symbol, url)
                                if data:
                                    self.tv_cache[symbol] = {
                                        "symbol": symbol,
                                        "price": data["valor"],
                                        "change": data["var"],
                                        "change_pct": data["var_pct"]
                                    }
                            except Exception as e:
                                logger.error(f"❌ Fallback Error {symbol}: {e}")
                        else:
                            logger.warning(f"⚠️ Sem URL de fallback para {symbol}")

                # Jitter to avoid pattern detection (120s + random 10-30s)
                sleep_time = 120 + random.randint(10, 30)
                logger.info(f"💤 Sleeping for {sleep_time}s...")
                await asyncio.sleep(sleep_time)

    async def _main_loop(self):
        """
        Main Aggregation Loop (Fast).
        Collects MT5 data (Realtime) + Cached Macro/TV/Calendar -> Redis.
        """
        while self.running:
            try:
                # 1. MT5 Data (Sync, fast local)
                mt5_data = await asyncio.to_thread(self.mt5.fetch_data)
                
                # Check for missing assets (Fallback Logic)
                # We check against MT5Client.TOP_ASSETS
                # mt5_data["blue_chips"] contains the ones successfully fetched
                found_symbols = set(mt5_data.get("blue_chips", {}).keys())
                expected_symbols = set(self.mt5.TOP_ASSETS)
                self.missing_in_mt5 = expected_symbols - found_symbols
                
                # 2. Aggregate
                # Calculate Volatility Regime (WIN) - Fast enough to do here or cache it
                # Since it uses D1 history, we can cache it, but for now let's compute on the fly if history is cached in MT5Client
                # Actually MT5Client fetches fresh history. Let's do it in _fetch_history_loop and cache it in DataEngine?
                # Simpler: Just call it here. It fetches 30 candles. Fast.
                volatility_regime = self.mt5.get_volatility_regime("WIN$N") or self.mt5.get_volatility_regime("WIN$")
                
                payload = {
                    "mt5": mt5_data,
                    "blue_chips": mt5_data.get("blue_chips", {}), # Expose at root for Frontend
                    "breadth": mt5_data.get("breadth", {}),       # Expose at root
                    "basis": mt5_data.get("basis", 0.0),          # Expose at root
                    "volatility": volatility_regime,              # New Field
                    "macro": self.macro_cache,
                    "tv": self.tv_cache,
                    "calendar": self.calendar_cache,
                    "timestamp": datetime.datetime.now().isoformat()
                }
                
                # 3. Publish
                self.redis.publish("market_data", payload)
                
                # Fast Interval (1s)
                await asyncio.sleep(BridgeConfig.FAST_INTERVAL)
                
            except Exception as e:
                logger.error(f"❌ Main Loop Error: {e}")
                await asyncio.sleep(1)

    async def _fetch_history_loop(self):
        """
        Loop for History Data (D1/H1).
        Runs every 5 minutes.
        """
        while self.running:
            logger.info("📜 Fetching History Data...")
            try:
                # WIN and WDO
                targets = ["WIN$N", "WDO$N"]
                timeframes = ["D1", "H1"]
                
                for symbol in targets:
                    for tf in timeframes:
                        # Run in thread to avoid blocking
                        data = await asyncio.to_thread(self.mt5.get_history, symbol, tf, 100)
                        if data:
                            key = f"history:{symbol}:{tf}"
                            self.redis.publish(key, data)
                            # logger.info(f"✅ History updated for {symbol} {tf}")
                        else:
                            logger.warning(f"⚠️ No history for {symbol} {tf}")
                            
            except Exception as e:
                logger.error(f"❌ History Loop Error: {e}")
            
            # Sleep for 5 minutes
            await asyncio.sleep(300)

    async def run(self):
        """
        Starts all async tasks.
        """
        logger.info("🚀 DataEngine Starting (Async Mode)...")
        
        await asyncio.gather(
            self._fetch_macro_loop(),
            self._fetch_calendar_loop(),
            self._fetch_global_loop(),
            self._fetch_history_loop(),
            self._main_loop()
        )

    def stop(self):
        self.running = False
        self.mt5.shutdown()
