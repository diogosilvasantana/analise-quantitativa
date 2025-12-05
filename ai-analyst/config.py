import os
from dotenv import load_dotenv

# Load environment variables from the root .env file (or local one)
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

class Config:
    # --- INFRAESTRUTURA ---
    # Backend URL (Onde pegamos dados técnicos e salvamos o relatório)
    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
    
    # Redis (Cache de dados rápidos)
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    
    # --- INTELIGÊNCIA ARTIFICIAL ---
    # Anthropic API Key (Claude 3.5 Sonnet)
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    
    # --- AGENDAMENTO ---
    # Horário "Golden Time" para análise de pré-abertura
    SCHEDULE_TIME = "08:45"
    
    # --- FONTES DE DADOS (RSS FEEDS) ---
    RSS_FEEDS = [
        # BRASIL: Mercado & Corporativo
        "https://www.infomoney.com.br/feed/",              # Resumo de abertura
        "https://braziljournal.com/feed/",                 # Análise profunda
        "https://br.investing.com/rss/news.rss",           # Notícias rápidas
        
        # BRASIL: Política (Risco Fiscal)
        "https://www.poder360.com.br/feed/",               # Congresso/Governo (Move Dólar)
        
        # GLOBAL: Sentimento Externo & Commodities
        "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664", # Economia Global
        "https://br.investing.com/rss/commodities.rss",    # Petróleo/Minério (Move Vale/Petro)
        
        # CRIPTO: Termômetro de Risco (Risk-On/Off)
        "https://cointelegraph.com.br/rss"
    ]
    
    # --- FILTRAGEM INTELIGENTE DE NOTÍCIAS ---
    # O coletor só aceitará notícias contendo estas palavras (Case Insensitive)
    NEWS_KEYWORDS = [
        # Ativos & Mercado
        "ibovespa", "dolar", "dólar", "win", "wdo", "mini indice", "mini dolar",
        "petrobras", "vale", "itau", "bradesco", "b3", "ewz", "adr",
        
        # Macroeconomia & Política
        "selic", "copom", "ipca", "inflação", "pib", "juros", "fed", "fomc", "payroll",
        "powell", "campos neto", "haddad", "lula", "arcabouço", "fiscal", "meta",
        
        # Commodities & Global
        "petróleo", "brent", "minério", "ferro", "ouro", "china", "eua", "europa",
        "guerra", "crise", "reserva federal", "stimulus"
    ]
    
    # Palavras para IGNORAR (Limpeza de ruído)
    IGNORE_KEYWORDS = [
        "bbb", "futebol", "novela", "famosos", "horóscopo", "loteria", 
        "mega-sena", "quiz", "teste", "review", "lançamento celular",
        "melhores destinos", "viagem", "promoção"
    ]

    # --- NOTIFICAÇÃO (Opcional) ---
    EMAIL_SENDER = os.getenv("EMAIL_SENDER")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
    EMAIL_RECIPIENTS = os.getenv("EMAIL_RECIPIENTS", "").split(",")