class ScraperError(Exception):
    """Exceção para erros de scraping."""
    pass

class MT5ConnectionError(Exception):
    """Exceção para erros de conexão com o MetaTrader 5."""
    pass

class CacheError(Exception):
    """Exceção para erros de cache."""
    pass
