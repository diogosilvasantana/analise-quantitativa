import logging
from loguru import logger
import sys
from src.config import LOG_LEVEL

def setup_logging():
    # Remove default handler for loguru to avoid duplicate logs
    logger.remove()
    
    # Add a new handler for console output
    logger.add(
        sys.stderr,
        level=LOG_LEVEL,
        format="{time} | {level: <8} | {name} - {message}",
        colorize=True,
        backtrace=True,
        diagnose=True
    )
    
    # Configure standard logging to use loguru
    logging.basicConfig(handlers=[LoguruHandler()], level=0)
    
    # Intercept standard library logging
    logging.getLogger("uvicorn").handlers = [LoguruHandler()]
    logging.getLogger("uvicorn.access").handlers = [LoguruHandler()]
    logging.getLogger("httpx").handlers = [LoguruHandler()]
    
    # Set loguru as the default logger for the root logger
    logging.getLogger().handlers = [LoguruHandler()]
    logging.getLogger().setLevel(LOG_LEVEL)

class LoguruHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelname
        
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        
        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())
