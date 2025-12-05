import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente (para Redis)
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', 'backend', '.env'))

class BridgeConfig:
    # Redis
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    if REDIS_HOST == "redis":
        REDIS_HOST = "localhost"
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    
    # Intervals
    SLOW_INTERVAL = 300  # 5 minutes for Macro Scraper
    FAST_INTERVAL = 1    # 1 second for MT5

    # MT5 Symbols (Blue Chips + DI + Futures)
    MT5_SYMBOLS = [
        "VALE3", "ITUB4", "PETR4", "WEGE3", "PETR3", 
        "BBDC4", "SBSP3", "BPAC11", "ITSA4", "B3SA3",
        "DI1F27", "DI1F29", "DI1F31", "WIN$N", "WDO$N", "IBOV"
    ]

    # Investing.com Targets
    # Investing.com Targets
    MACRO_TARGETS = {
        # Índices Globais
        "SP500": "https://br.investing.com/indices/us-spx-500",
        "NASDAQ": "https://br.investing.com/indices/nq-100-futures", # NQ 100 Futures (Tech)
        "DXY": "https://br.investing.com/indices/usdollar",
        "DOW_JONES": "https://br.investing.com/indices/us-30",
        "DAX40": "https://br.investing.com/indices/germany-30",
        "US10Y": "https://br.investing.com/rates-bonds/u.s.-10-year-bond-yield",
        "EWZ": "https://br.investing.com/etfs/ishares-brazil-index",
        "PBR": "https://br.investing.com/equities/petroleo-brasileiro-sa-petrobras-adr",
        "VALE_ADR": "https://br.investing.com/equities/vale-s.a.--adr",
        
        # Commodities
        "BRENT": "https://br.investing.com/commodities/brent-oil",
        "OURO": "https://br.investing.com/commodities/gold",
        "COBRE": "https://br.investing.com/commodities/copper",
        "MINERIO_FERRO": "https://br.investing.com/commodities/iron-ore-62-cfr-futures",
        
        # Taxas
        "CUPOM_LIMPO": "https://br.investing.com/rates-bonds/brazil-10-year-bond-yield",
        "PTAX": "https://economia.awesomeapi.com.br/json/last/USD-BRL",
    }
