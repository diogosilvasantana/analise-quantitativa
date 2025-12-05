from pydantic import BaseModel
from typing import Dict, Optional, List, Any
from datetime import datetime

class IndiceData(BaseModel):
    valor: float
    var: float
    var_pct: Optional[float] = None
    ajuste: Optional[float] = None # New field for Adjustment Price
    timestamp: Optional[str] = None

class IndicesGlobais(BaseModel):
    SP500: Optional[IndiceData] = None
    NASDAQ: Optional[IndiceData] = None
    DOW_JONES: Optional[IndiceData] = None
    DXY: Optional[IndiceData] = None
    DAX40: Optional[IndiceData] = None
    US10Y: Optional[IndiceData] = None
    EWZ: Optional[IndiceData] = None
    PBR: Optional[IndiceData] = None # Petrobras ADR
    VALE_ADR: Optional[IndiceData] = None # Vale ADR

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
    DI_MT5: Optional[IndiceData] = None # DI1F27
    DI1F29: Optional[IndiceData] = None # DI1F29

class CalendarEvent(BaseModel):
    time: str
    currency: str
    impact: int
    event: str
    actual: str
    forecast: str
    previous: str

class MarketBreadth(BaseModel):
    up: int
    down: int
    neutral: int
    signal: str = "NEUTRAL"
    confidence: float = 0.0
    details: Optional[Dict[str, float]] = None

class BasisData(BaseModel):
    value: float
    interpretation: str
    diff_yesterday: float = 0.0

class SentimentComparison(BaseModel):
    spx_signal: str
    win_signal: str
    divergence: bool
    status: str

class VolatilityRegime(BaseModel):
    status: str
    ratio: float
    atr5: float
    atr20: float
    implication: str

class DashboardData(BaseModel):
    indices_globais: IndicesGlobais
    commodities: Commodities
    blue_chips: IBOVTop10
    taxas: Taxas
    calendar: List[CalendarEvent] = []
    breadth: Optional[MarketBreadth] = None
    basis: Optional[BasisData] = None
    volatility: Optional[VolatilityRegime] = None # New Field
    sentiment_comparison: Optional[SentimentComparison] = None
    signal_history: List[Dict[str, str]] = []
    ai_analysis: Optional[Dict[str, Any]] = None
    win: Optional[IndiceData] = None # Snapshot WIN
    wdo: Optional[IndiceData] = None # Snapshot WDO
    timestamp: str
    formatted_time: str
