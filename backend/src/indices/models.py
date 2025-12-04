from pydantic import BaseModel
from typing import Dict, Optional, List
from datetime import datetime

class IndiceData(BaseModel):
    valor: float
    var: float
    var_pct: Optional[float] = None
    timestamp: Optional[str] = None

class IndicesGlobais(BaseModel):
    SP500: Optional[IndiceData] = None
    NASDAQ: Optional[IndiceData] = None
    DOW_JONES: Optional[IndiceData] = None
    DXY: Optional[IndiceData] = None
    DAX40: Optional[IndiceData] = None
    US10Y: Optional[IndiceData] = None
    EWZ: Optional[IndiceData] = None

class Commodities(BaseModel):
    BRENT: Optional[IndiceData] = None
    OURO: Optional[IndiceData] = None
    COBRE: Optional[IndiceData] = None
    MINERIO_FERRO: Optional[IndiceData] = None

class IBOVTop10(BaseModel):
    # 1. Commodities (Peso Pesado)
    VALE3: Optional[IndiceData] = None  # Minério
    PETR4: Optional[IndiceData] = None  # Petróleo

    # 2. Bancos (Peso Pesado)
    ITUB4: Optional[IndiceData] = None  # Privado Líder
    BBDC4: Optional[IndiceData] = None  # Privado Varejo
    BBAS3: Optional[IndiceData] = None  # Estatal (Risco Gov)

    # 3. Indústria & Dólar
    WEGE3: Optional[IndiceData] = None  # Exportadora (Hedge)

    # 4. Utilities (Substituindo ELET3/AXIA3)
    SBSP3: Optional[IndiceData] = None  # Sabesp (Saneamento/Privatização)

    # 5. Ciclo Doméstico (Juros e Consumo)
    RENT3: Optional[IndiceData] = None  # Localiza (Sensível a Juros)
    LREN3: Optional[IndiceData] = None  # Renner (Varejo Puro)

    # 6. Financeiro/Beta
    B3SA3: Optional[IndiceData] = None  # B3 (Alta Volatilidade)

class Taxas(BaseModel):
    CUPOM_LIMPO: Optional[IndiceData] = None
    PTAX: Optional[IndiceData] = None
    DI_MT5: Optional[IndiceData] = None # DI vindo do MT5

class CalendarEvent(BaseModel):
    time: str
    currency: str
    impact: int
    event: str
    actual: str
    forecast: str
    previous: str

class DashboardData(BaseModel):
    indices_globais: IndicesGlobais
    commodities: Commodities
    blue_chips: IBOVTop10
    taxas: Taxas
    calendar: List[CalendarEvent] = []
    timestamp: str
