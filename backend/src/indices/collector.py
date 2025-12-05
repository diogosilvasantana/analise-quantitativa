import asyncio
import logging
import json
from src.cache.redis_manager import RedisManager
from src.indices.models import DashboardData, IndicesGlobais, Commodities, IBOVTop10, Taxas, IndiceData, CalendarEvent, MarketBreadth, BasisData
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class IndicesCollector:
    def __init__(self, redis_manager: RedisManager):
        self.redis = redis_manager
        
        # Mapeamento para organizar os dados do Redis (macro) nas categorias certas
        self.indices_map = ["SP500", "NASDAQ", "DXY", "DOW_JONES", "DAX40", "US10Y", "EWZ", "PBR", "VALE_ADR"]
        self.commodities_map = ["BRENT", "OURO", "COBRE", "MINERIO_FERRO"]
        self.taxas_map = ["CUPOM_LIMPO", "PTAX"]
        
        # State for Signal History
        self.signal_history = []

    def _calculate_spx_signal(self, sp500_data: IndiceData) -> str:
        if not sp500_data or sp500_data.var_pct is None:
            return "NEUTRAL"
        
        pct = sp500_data.var_pct
        if pct > 0.1: return "BUY"
        if pct < -0.1: return "SELL"
        return "NEUTRAL"

    def _update_history(self, current_signal: str, timestamp: str):
        # Only add if signal changed
        if not self.signal_history or self.signal_history[-1]["signal"] != current_signal:
            self.signal_history.append({"time": timestamp, "signal": current_signal})
            # Keep last 5
            if len(self.signal_history) > 5:
                self.signal_history.pop(0)

    async def collect_all(self) -> DashboardData:
        """
        Coleta dados agregados do Redis (enviados pelo bridge.py).
        """
        indices_data = {}
        commodities_data = {}
        taxas_data = {}
        blue_chips_data = {}
        breadth_data = None
        basis_value = None
        sentiment_comparison = None
        
        try:
            # Lê o JSON agregado do Redis
            raw_data = await self.redis.get("market_data")
            
            if raw_data:
                data = json.loads(raw_data)
                macro = data.get("macro", {})
                mt5 = data.get("mt5", {})
                
                # 1. Processa Macro Data (Indices, Commodities, Taxas)
                for name in self.indices_map:
                    if name in macro and macro[name]:
                        indices_data[name] = IndiceData(**macro[name])
                        
                for name in self.commodities_map:
                    if name in macro and macro[name]:
                        commodities_data[name] = IndiceData(**macro[name])
                        
                for name in self.taxas_map:
                    if name in macro and macro[name]:
                        taxas_data[name] = IndiceData(**macro[name])
                
                # 2. Processa MT5 Data (Blue Chips, DI)
                raw_blue_chips = data.get("blue_chips", {})
                for symbol, item in raw_blue_chips.items():
                    if item:
                        blue_chips_data[symbol] = IndiceData(**item)
                        
                # DI do MT5 (DI1F27 e DI1F29)
                if "DI1F27" in mt5 and mt5["DI1F27"]:
                     taxas_data["DI_MT5"] = IndiceData(**mt5["DI1F27"])
                if "DI1F29" in mt5 and mt5["DI1F29"]:
                     taxas_data["DI1F29"] = IndiceData(**mt5["DI1F29"])

                # 3. Processa Calendar Data
                calendar_events = []
                if "calendar" in data and data["calendar"]:
                    for event in data["calendar"]:
                        calendar_events.append(CalendarEvent(**event))
                
                # 4. Breadth & Basis
                if "breadth" in data and data["breadth"]:
                    breadth_data = MarketBreadth(**data["breadth"])
                    
                    # Calculate Confidence
                    total = breadth_data.up + breadth_data.down + breadth_data.neutral
                    if total > 0:
                        # Confidence based on majority direction strength
                        majority = max(breadth_data.up, breadth_data.down)
                        breadth_data.confidence = (majority / 10.0) * 100.0
                
                if "basis" in data:
                    if isinstance(data["basis"], dict):
                        basis_value = BasisData(**data["basis"])
                    else:
                        basis_value = BasisData(value=float(data["basis"]), interpretation="LEGACY")

                # 5. Advanced Sentiment Logic (Comparison & History)
                current_time = datetime.now(timezone(timedelta(hours=-3))).strftime("%H:%M:%S")
                
                # SPX Signal
                spx_signal = "NEUTRAL"
                if "SP500" in indices_data:
                    spx_signal = self._calculate_spx_signal(indices_data["SP500"])
                
                # WIN Signal (from Breadth)
                win_signal = breadth_data.signal if breadth_data else "NEUTRAL"
                
                # Divergence Check
                # Simple logic: Opposing directions
                divergence = False
                if ("BUY" in spx_signal and "SELL" in win_signal) or \
                   ("SELL" in spx_signal and "BUY" in win_signal):
                    divergence = True
                
                status = "DIVERGÊNCIA ⚠️" if divergence else "ALINHADO ✅"
                
                sentiment_comparison = {
                    "spx_signal": spx_signal,
                    "win_signal": win_signal,
                    "divergence": divergence,
                    "status": status
                }
                
                # Update History
                self._update_history(win_signal, current_time)

            else:
                pass

        except Exception as e:
            logger.error(f"❌ Erro ao processar dados do Redis: {e}")

        # 6. AI Analysis Report
        ai_analysis = None
        try:
            raw_ai = await self.redis.get("ai_analyst_report")
            if raw_ai:
                ai_analysis = json.loads(raw_ai)
        except Exception as e:
            logger.error(f"❌ Erro ao buscar AI report: {e}")

        # Extract WIN/WDO snapshots from MT5 data if available
        win_snapshot = None
        wdo_snapshot = None
        if raw_data:
            data = json.loads(raw_data)
            mt5 = data.get("mt5", {})
            # Try standard keys
            if "WIN$N" in mt5: win_snapshot = IndiceData(**mt5["WIN$N"])
            elif "WIN$" in mt5: win_snapshot = IndiceData(**mt5["WIN$"])
            
            if "WDO$N" in mt5: wdo_snapshot = IndiceData(**mt5["WDO$N"])
            elif "WDO$" in mt5: wdo_snapshot = IndiceData(**mt5["WDO$"])

        # Monta o objeto final
        dashboard_data = DashboardData(
            indices_globais=IndicesGlobais(**indices_data),
            commodities=Commodities(**commodities_data),
            blue_chips=IBOVTop10(**blue_chips_data),
            taxas=Taxas(**taxas_data),
            calendar=calendar_events,
            breadth=breadth_data,
            basis=basis_value,
            sentiment_comparison=sentiment_comparison,
            signal_history=self.signal_history,
            ai_analysis=ai_analysis,
            win=win_snapshot,
            wdo=wdo_snapshot,
            timestamp=datetime.now(timezone(timedelta(hours=-3))).isoformat(),
            formatted_time=datetime.now(timezone(timedelta(hours=-3))).strftime("%H:%M:%S")
        )
        
        # Salva em cache para API
        await self.redis.set("dashboard_data", dashboard_data.model_dump_json(), ttl=self.redis.ttl)
        
        return dashboard_data
