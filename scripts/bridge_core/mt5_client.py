import MetaTrader5 as mt5
import logging
import datetime
from .config import BridgeConfig

logger = logging.getLogger("Bridge.MT5")

class MT5Client:
    def __init__(self):
        self.connected = False
        self.TOP_ASSETS = [
            "VALE3", "PETR4", "ITUB4", "BBDC4", "BBAS3", 
            "WEGE3", "SBSP3", "RENT3", "LREN3", "B3SA3"
        ]
        self.connect()

    def connect(self):
        if not mt5.initialize():
            logger.error(f"❌ MT5 Init Failed: {mt5.last_error()}")
            self.connected = False
        else:
            logger.info("✅ MT5 Inicializado com sucesso")
            self.connected = True
            self._ensure_symbols()

    def _ensure_symbols(self):
        # Ensure main symbols + Top 10 are selected
        all_symbols = BridgeConfig.MT5_SYMBOLS + self.TOP_ASSETS + ["IBOV"]
        for symbol in all_symbols:
            if not mt5.symbol_select(symbol, True):
                logger.warning(f"⚠️ Símbolo {symbol} não encontrado no MT5")

    def get_market_breadth(self):
        """
        Calculates Market Breadth (Top 10 Assets).
        Returns: { "up": int, "down": int, "neutral": int }
        """
        up, down, neutral = 0, 0, 0
        details = {}

        for symbol in self.TOP_ASSETS:
            # Force selection to ensure data availability
            if not mt5.symbol_select(symbol, True):
                logger.warning(f"⚠️ Falha ao selecionar {symbol} no MT5")

            tick = mt5.symbol_info_tick(symbol)
            info = mt5.symbol_info(symbol)
            
            if tick and info and info.session_close > 0:
                change = tick.last - info.session_close
                if change > 0: up += 1
                elif change < 0: down += 1
                else: neutral += 1
                
                details[symbol] = (change / info.session_close) * 100
            else:
                neutral += 1
        
        return {
            "up": up,
            "down": down,
            "neutral": neutral,
            "details": details
        }

    def get_basis(self):
        """
        Calculates Basis (Spread) = WIN - IBOV.
        """
        try:
            # Assuming WIN$ or current contract
            win_tick = mt5.symbol_info_tick("WIN$") # Or specific contract
            ibov_tick = mt5.symbol_info_tick("IBOV")
            
            if win_tick and ibov_tick:
                return win_tick.last - ibov_tick.last
            return 0.0
        except:
            return 0.0

    def fetch_data(self):
        data = {}
        if not self.connected:
            if not mt5.initialize():
                return {}
            self.connected = True

        # 1. Main Symbols (WIN, WDO, DI)
        for symbol in BridgeConfig.MT5_SYMBOLS:
            try:
                tick = mt5.symbol_info_tick(symbol)
                info = mt5.symbol_info(symbol)
                
                price = 0.0
                if tick and tick.last > 0:
                    price = tick.last
                elif info:
                    price = info.session_close if info.session_close > 0 else info.last

                # Calculate Change
                change = 0.0
                change_pct = 0.0
                
                if info and info.session_close > 0 and price > 0:
                    change = price - info.session_close
                    change_pct = (change / info.session_close) * 100
                
                # Adjustment Price (Ajuste)
                ajuste = 0.0
                if info:
                    # Try settlement price first (Ajuste oficial)
                    if hasattr(info, 'session_price_settlement') and info.session_price_settlement > 0:
                        ajuste = info.session_price_settlement
                    # Fallback to Weighted Average if settlement not available (rare for Futures)
                    elif hasattr(info, 'session_aw') and info.session_aw > 0:
                        ajuste = info.session_aw

                data[symbol] = {
                    "valor": price,
                    "var": change,
                    "var_pct": change_pct,
                    "ajuste": ajuste,
                    "timestamp": datetime.datetime.now().isoformat()
                }
            except Exception:
                pass
        
        # 2. Blue Chips (TOP_ASSETS)
        blue_chips = {}
        up, down, neutral = 0, 0, 0
        
        for symbol in self.TOP_ASSETS:
            # Force selection
            if not mt5.symbol_select(symbol, True):
                logger.warning(f"⚠️ Falha ao selecionar {symbol}")

            tick = mt5.symbol_info_tick(symbol)
            info = mt5.symbol_info(symbol)
            
            # Use tick if available, else info (last price)
            price = 0.0
            if tick and tick.last > 0:
                price = tick.last
            elif info:
                price = info.session_close if info.session_close > 0 else info.last
            
            if price > 0 and info and info.session_close > 0:
                change = price - info.session_close
                change_pct = (change / info.session_close) * 100
                
                blue_chips[symbol] = {
                    "valor": price,
                    "var": change,
                    "var_pct": change_pct
                }
                
                # DEBUG: Log specific assets to find the "wrong percentage" cause
                if symbol in ["VALE3", "PETR4"]:
                     logger.info(f"🔍 {symbol}: Price={price}, Close={info.session_close}, Calc_Pct={change_pct:.2f}%")
                
                if change > 0: up += 1
                elif change < 0: down += 1
                else: neutral += 1
            else:
                neutral += 1
                # Don't add to blue_chips if no data, so DataEngine detects it as missing
        
        data["blue_chips"] = blue_chips
        
        # 3. Breadth (Calculated from Blue Chips)
        # Signal Logic: Check for Divergence
        # If WIN is UP (>0.2%) but Breadth is WEAK (<5 UP) -> BEARISH DIVERGENCE
        # If WIN is DOWN (<-0.2%) but Breadth is STRONG (>5 UP) -> BULLISH DIVERGENCE
        
        win_data = data.get("WIN$N") or data.get("WIN$") or data.get("WINZ25")
        win_pct = win_data.get("var_pct", 0.0) if win_data else 0.0
        
        signal = "NEUTRAL"
        if win_pct > 0.2 and up < 5:
            signal = "BEARISH_DIVERGENCE"
        elif win_pct < -0.2 and up > 5:
            signal = "BULLISH_DIVERGENCE"
        elif up >= 7:
            signal = "STRONG_BUY"
        elif down >= 7:
            signal = "STRONG_SELL"
        elif up > down:
            signal = "BUY"
        elif down > up:
            signal = "SELL"

        data["breadth"] = {
            "up": up,
            "down": down,
            "neutral": neutral,
            "signal": signal,
            "details": {k: v["var_pct"] for k, v in blue_chips.items()}
        }
        
        # 3. Basis (WIN - IBOV)
        basis_val = 0.0
        interpretation = "NEUTRAL"
        
        try:
            win = win_data.get("valor", 0) if win_data else 0
            ibov = data.get("IBOV", {}).get("valor", 0)
            
            if win > 0 and ibov > 0:
                basis_val = win - ibov
                
                # Interpretation Logic
                if basis_val > 1500:
                    interpretation = "PREMIUM_HIGH" # Muito otimista
                elif basis_val > 500:
                    interpretation = "PREMIUM_NORMAL" # Normal (Juros)
                elif basis_val < -500:
                    interpretation = "DISCOUNT_HIGH" # Pessimismo extremo
                elif basis_val < 0:
                    interpretation = "DISCOUNT" # Backwardation
                else:
                    interpretation = "FLAT"
            else:
                logger.warning(f"⚠️ Basis Incompleto: WIN={win} (Sym: {win_data}), IBOV={ibov}")
                
        except Exception as e:
            logger.error(f"❌ Erro Basis: {e}")

        data["basis"] = {
            "value": basis_val,
            "interpretation": interpretation,
            "diff_yesterday": 0.0 # Placeholder for now
        }
        
        # DEBUG: Log Top Assets details to understand percentage calculation
        if "VALE3" in blue_chips:
            v = blue_chips["VALE3"]
            # logger.info(f"🔍 DEBUG VALE3: Price={v['valor']}, Var={v['var']}, Pct={v['var_pct']:.2f}%")
            
        return data

    def shutdown(self):
        mt5.shutdown()

    def get_history(self, symbol: str, timeframe_str: str, count: int = 100):
        """
        Fetches historical data from MT5.
        timeframe_str: "D1", "H1", "M5", etc.
        """
        if not self.connected:
            if not mt5.initialize():
                return []
            self.connected = True

        # Map string to MT5 constant
        tf_map = {
            "D1": mt5.TIMEFRAME_D1,
            "H1": mt5.TIMEFRAME_H1,
            "M5": mt5.TIMEFRAME_M5,
            "M1": mt5.TIMEFRAME_M1
        }
        
        tf = tf_map.get(timeframe_str, mt5.TIMEFRAME_D1)
        
        # Ensure symbol is selected
        if not mt5.symbol_select(symbol, True):
             logger.warning(f"⚠️ Símbolo {symbol} não encontrado para histórico")
             return []

        rates = mt5.copy_rates_from_pos(symbol, tf, 0, count)
        
        if rates is None:
            logger.warning(f"⚠️ Sem histórico para {symbol}")
            return []
            
        data = []
        for rate in rates:
            data.append({
                "time": int(rate['time']),
                "open": float(rate['open']),
                "high": float(rate['high']),
                "low": float(rate['low']),
                "close": float(rate['close']),
                "tick_volume": int(rate['tick_volume']),
                "real_volume": int(rate['real_volume'])
            })
        return data
