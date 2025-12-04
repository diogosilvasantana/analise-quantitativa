import asyncio
import logging
import json
from src.cache.redis_manager import RedisManager
from src.indices.models import DashboardData, IndicesGlobais, Commodities, IBOVTop10, Taxas, IndiceData, CalendarEvent
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class IndicesCollector:
    def __init__(self, redis_manager: RedisManager):
        self.redis = redis_manager
        
        # Mapeamento para organizar os dados do Redis (macro) nas categorias certas
        # Mapeamento para organizar os dados do Redis (macro) nas categorias certas
        self.indices_map = ["SP500", "NASDAQ", "DXY", "DOW_JONES", "DAX40", "US10Y", "EWZ"]
        self.commodities_map = ["BRENT", "OURO", "COBRE", "MINERIO_FERRO"]
        self.taxas_map = ["CUPOM_LIMPO", "PTAX"]
        
        # Blue Chips (MT5) - Dinâmico via Redis
        # self.blue_chips_symbols removido para aceitar o que vier do Bridge

    async def collect_all(self) -> DashboardData:
        """
        Coleta dados agregados do Redis (enviados pelo bridge.py).
        """
        indices_data = {}
        commodities_data = {}
        taxas_data = {}
        blue_chips_data = {}
        
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
                # Pega diretamente do payload 'blue_chips' que o DataEngine envia
                raw_blue_chips = data.get("blue_chips", {})
                for symbol, item in raw_blue_chips.items():
                    if item:
                        blue_chips_data[symbol] = IndiceData(**item)
                        
                # DI do MT5
                if "DI1F27" in mt5 and mt5["DI1F27"]:
                     # Mapeia DI1F27 para DI_MT5 ou usa o nome direto se preferir
                     taxas_data["DI_MT5"] = IndiceData(**mt5["DI1F27"])

                # 3. Processa Calendar Data
                calendar_events = []
                if "calendar" in data and data["calendar"]:
                    for event in data["calendar"]:
                        calendar_events.append(CalendarEvent(**event))

            else:
                # logger.warning("⚠️ Aguardando dados do Bridge (scripts/bridge.py)...")
                pass

        except Exception as e:
            logger.error(f"❌ Erro ao processar dados do Redis: {e}")

        # Monta o objeto final
        dashboard_data = DashboardData(
            indices_globais=IndicesGlobais(**indices_data),
            commodities=Commodities(**commodities_data),
            blue_chips=IBOVTop10(**blue_chips_data),
            taxas=Taxas(**taxas_data),
            calendar=calendar_events,
            timestamp=datetime.now().isoformat()
        )
        
        # Salva em cache para API (opcional, já que lemos do Redis, mas mantém padrão)
        await self.redis.set("dashboard_data", dashboard_data.model_dump_json(), ttl=self.redis.ttl)
        
        return dashboard_data
