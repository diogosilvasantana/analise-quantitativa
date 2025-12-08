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
from .flow_monitor import FlowMonitor
from .profit_bridge import ProfitBridge

logger = logging.getLogger("Bridge.DataEngine")

class DataEngine:
    def __init__(self):
        self.running = True
        
        # Clients
        self.mt5 = MT5Client()
        self.investing = InvestingClient()
        self.calendar = CalendarClient()
        self.redis = RedisClient()
        self.flow_monitor = FlowMonitor()
        
        # Profit Pro RTD Bridge (optional, will fail gracefully if Excel not open)
        try:
            self.profit = ProfitBridge("profit-data.xlsx")
            logger.info("✅ Profit Pro RTD connected")
        except Exception as e:
            logger.warning(f"⚠️ Profit Pro RTD not available: {e}")
            self.profit = None
        
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
        If Profit Pro RTD is available, uses its calculated indicators.
        """
        while self.running:
            try:
                # 1. MT5 Data (Sync, fast local)
                mt5_data = await asyncio.to_thread(self.mt5.fetch_data)
                
                # 1.5. Profit Pro RTD Data (if available)
                profit_data = None
                if self.profit:
                    try:
                        profit_data = await asyncio.to_thread(self.profit.get_data)
                        logger.debug("📊 Profit Pro RTD data fetched")
                    except Exception as e:
                        logger.warning(f"⚠️ Error reading Profit RTD: {e}")
                
                # Check for missing assets (Fallback Logic)
                # We check against MT5Client.TOP_ASSETS
                # mt5_data["blue_chips"] contains the ones successfully fetched
                found_symbols = set(mt5_data.get("blue_chips", {}).keys())
                expected_symbols = set(self.mt5.TOP_ASSETS)
                self.missing_in_mt5 = expected_symbols - found_symbols
                
                # 2. Aggregate
                # Calculate Volatility Regime (WIN)
                volatility_regime = self.mt5.get_volatility_regime("WIN$N") or self.mt5.get_volatility_regime("WIN$")
                
                # Check Flow Data
                flow_data = self.flow_monitor.check_update() or self.flow_monitor.current_flows
                
                # 3. Quant Score Calculation
                # If Profit Pro RTD is available, use its pre-calculated scores
                # Otherwise, calculate manually
                if profit_data and profit_data.get("win") and profit_data.get("wdo"):
                    # Use Profit Pro RTD scores directly
                    quant_score = {
                        "WIN": {
                            "score": profit_data["win"].get("score", 0),
                            "bull_power": profit_data["win"].get("bull_power", 0),
                            "bear_power": profit_data["win"].get("bear_power", 0),
                            "max_score": 15,
                            "details": [f"Profit Pro: {profit_data['win'].get('decision', 'N/A')}"],
                            "sentiment": self._get_sentiment(profit_data["win"].get("decision", "")),
                            "status": profit_data["win"].get("decision", "AGUARDAR"),
                            "direction": self._get_direction(profit_data["win"].get("decision", ""))
                        },
                        "WDO": {
                            "score": profit_data["wdo"].get("score", 0),
                            "bull_power": profit_data["wdo"].get("bull_power", 0),
                            "bear_power": profit_data["wdo"].get("bear_power", 0),
                            "max_score": 15,
                            "details": [f"Profit Pro: {profit_data['wdo'].get('decision', 'N/A')}"],
                            "sentiment": self._get_sentiment(profit_data["wdo"].get("decision", "")),
                            "status": profit_data["wdo"].get("decision", "AGUARDAR"),
                            "direction": self._get_direction(profit_data["wdo"].get("decision", ""))
                        }
                    }
                    logger.info("✅ Using Profit Pro RTD scores")
                else:
                    # Fallback to manual calculation
                    quant_score = self.flow_monitor.calculate_quant_score(
                        flow_data, 
                        {**self.macro_cache, **mt5_data},  # Merge macro cache with MT5 data (includes WDO, DI)
                        mt5_data.get("blue_chips", {}),
                        self.mt5  # Pass MT5Client instance
                    )
                    logger.debug("📊 Using manual score calculation")
                
                payload = {
                    "mt5": mt5_data,
                    "blue_chips": mt5_data.get("blue_chips", {}), 
                    "breadth": mt5_data.get("breadth", {}),       
                    "basis": mt5_data.get("basis", 0.0),          
                    "volatility": volatility_regime,
                    "quant_dashboard": {
                        "flows": flow_data, # Renamed to flows (plural) to indicate dict of assets
                        "score": quant_score,
                        "source": "profit_pro" if profit_data else "manual"  # Indicate data source
                    },
                    "profit_rtd": profit_data,  # Include raw Profit Pro data
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

    def _get_sentiment(self, decision: str) -> str:
        """Convert Profit Pro decision text to sentiment."""
        decision_upper = decision.upper()
        if "COMPRA" in decision_upper:
            return "BULLISH"
        elif "VENDA" in decision_upper:
            return "BEARISH"
        else:
            return "NEUTRAL"
    
    def _get_direction(self, decision: str) -> str:
        """Convert Profit Pro decision text to direction."""
        decision_upper = decision.upper()
        if "COMPRA" in decision_upper:
            return "BUY"
        elif "VENDA" in decision_upper:
            return "SELL"
        else:
            return "NEUTRAL"

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
