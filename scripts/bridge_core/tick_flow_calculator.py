"""
MT5 Tick Flow Calculator
=========================
Calcula o fluxo de agressão (Trade Radar) usando dados de ticks do MT5.
Substitui a necessidade do Profit Pro para análise de fluxo.

Author: AI Trader Pro
Date: 2025-12-06
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger("Bridge.TickFlow")


class TickFlowCalculator:
    """
    Calcula fluxo de agressão (compra vs venda) usando ticks do MT5.
    
    Substitui o "Trade Radar" do Profit Pro analisando cada negócio
    e identificando se foi agressão compradora ou vendedora.
    """
    
    def __init__(self):
        self.cache = {}  # Cache de fluxo acumulado
        self.last_update = {}
    
    def calculate_aggression_flow(self, symbol: str, period_minutes: int = 60) -> dict:
        """
        Calcula o saldo de agressão (comprador - vendedor) para um símbolo.
        
        Args:
            symbol: Símbolo do ativo (ex: "WIN$N")
            period_minutes: Período em minutos para análise
            
        Returns:
            Dict com volume de compra, venda e saldo
        """
        try:
            # Pega ticks desde o início do período
            now = datetime.now()
            from_time = now - timedelta(minutes=period_minutes)
            
            # Copia ticks de negócios (COPY_TICKS_TRADE)
            ticks = mt5.copy_ticks_range(symbol, from_time, now, mt5.COPY_TICKS_TRADE)
            
            if ticks is None or len(ticks) == 0:
                logger.warning(f"⚠️ Sem ticks para {symbol}")
                return {"buy": 0, "sell": 0, "net": 0, "total_ticks": 0}
            
            df = pd.DataFrame(ticks)
            
            # Análise de flags de agressão
            # TICK_FLAG_BUY (0x2) = Comprador agrediu (bateu na oferta de venda)
            # TICK_FLAG_SELL (0x4) = Vendedor agrediu (bateu na oferta de compra)
            
            buy_volume = 0
            sell_volume = 0
            
            for _, tick in df.iterrows():
                volume = tick['volume']
                flags = tick['flags']
                
                # Verifica flags bitwise
                if flags & mt5.TICK_FLAG_BUY:
                    buy_volume += volume
                elif flags & mt5.TICK_FLAG_SELL:
                    sell_volume += volume
            
            net_flow = buy_volume - sell_volume
            
            logger.debug(f"📊 {symbol} Flow: Buy={buy_volume}, Sell={sell_volume}, Net={net_flow}")
            
            return {
                "buy": int(buy_volume),
                "sell": int(sell_volume),
                "net": int(net_flow),
                "total_ticks": len(df)
            }
            
        except Exception as e:
            logger.error(f"❌ Erro calculando fluxo para {symbol}: {e}")
            return {"buy": 0, "sell": 0, "net": 0, "total_ticks": 0}
    
    def calculate_intraday_flow(self, symbol: str) -> dict:
        """
        Calcula fluxo acumulado desde a abertura do dia.
        
        Args:
            symbol: Símbolo do ativo
            
        Returns:
            Dict com fluxo do dia
        """
        try:
            # Início do dia (09:00)
            now = datetime.now()
            today_start = datetime(now.year, now.month, now.day, 9, 0, 0)
            
            # Se ainda não abriu o mercado, retorna zero
            if now < today_start:
                return {"buy": 0, "sell": 0, "net": 0, "total_ticks": 0}
            
            # Copia ticks desde a abertura
            ticks = mt5.copy_ticks_range(symbol, today_start, now, mt5.COPY_TICKS_TRADE)
            
            if ticks is None or len(ticks) == 0:
                return {"buy": 0, "sell": 0, "net": 0, "total_ticks": 0}
            
            df = pd.DataFrame(ticks)
            
            buy_volume = df[df['flags'] & mt5.TICK_FLAG_BUY]['volume'].sum()
            sell_volume = df[df['flags'] & mt5.TICK_FLAG_SELL]['volume'].sum()
            
            return {
                "buy": int(buy_volume),
                "sell": int(sell_volume),
                "net": int(buy_volume - sell_volume),
                "total_ticks": len(df)
            }
            
        except Exception as e:
            logger.error(f"❌ Erro calculando fluxo intraday para {symbol}: {e}")
            return {"buy": 0, "sell": 0, "net": 0, "total_ticks": 0}
    
    def get_flow_classification(self, net_flow: int, avg_volume: float) -> str:
        """
        Classifica a intensidade do fluxo.
        
        Args:
            net_flow: Fluxo líquido (compra - venda)
            avg_volume: Volume médio de referência
            
        Returns:
            Classificação: "FORTE", "MODERADO", "FRACO", "NEUTRO"
        """
        if avg_volume == 0:
            return "NEUTRO"
        
        ratio = abs(net_flow) / avg_volume
        
        if ratio > 0.5:
            return "FORTE"
        elif ratio > 0.2:
            return "MODERADO"
        elif ratio > 0.05:
            return "FRACO"
        else:
            return "NEUTRO"


# Função helper para integração com flow_monitor.py existente
def get_mt5_flow_data(symbol: str) -> dict:
    """
    Função helper para obter dados de fluxo formatados para flow_monitor.
    
    Args:
        symbol: Símbolo do ativo
        
    Returns:
        Dict compatível com flow_monitor (FOREIGN, INSTITUTIONAL, RETAIL)
    """
    calculator = TickFlowCalculator()
    
    # Calcula fluxo de 1 hora
    flow_1h = calculator.calculate_aggression_flow(symbol, period_minutes=60)
    
    # Simula classificação por tamanho de ordem
    # Ordens grandes (>100 contratos) = Gringo
    # Ordens médias (20-100) = Institucional
    # Ordens pequenas (<20) = Varejo
    
    # Por enquanto, usamos o fluxo total como "FOREIGN"
    # TODO: Implementar análise de tamanho de ordem quando disponível
    
    return {
        "FOREIGN": flow_1h["net"],  # Fluxo líquido total
        "INSTITUTIONAL": 0,  # Placeholder
        "RETAIL": 0  # Placeholder
    }


if __name__ == "__main__":
    # Teste standalone
    import logging
    logging.basicConfig(level=logging.INFO)
    
    if not mt5.initialize():
        print("❌ Erro ao inicializar MT5")
        quit()
    
    print("=" * 60)
    print("MT5 Tick Flow Calculator - Test Mode")
    print("=" * 60)
    
    calculator = TickFlowCalculator()
    
    # Teste com WIN
    print("\n📊 WIN (Mini Índice)")
    flow_win = calculator.calculate_aggression_flow("WIN$N", period_minutes=60)
    print(f"   Compra: {flow_win['buy']:,}")
    print(f"   Venda: {flow_win['sell']:,}")
    print(f"   Saldo: {flow_win['net']:,}")
    print(f"   Total Ticks: {flow_win['total_ticks']:,}")
    
    # Teste com WDO
    print("\n💵 WDO (Mini Dólar)")
    flow_wdo = calculator.calculate_aggression_flow("WDO$N", period_minutes=60)
    print(f"   Compra: {flow_wdo['buy']:,}")
    print(f"   Venda: {flow_wdo['sell']:,}")
    print(f"   Saldo: {flow_wdo['net']:,}")
    print(f"   Total Ticks: {flow_wdo['total_ticks']:,}")
    
    mt5.shutdown()
