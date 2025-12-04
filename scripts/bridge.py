import asyncio
import logging
import sys
import os

# Add 'scripts' directory to path so we can import bridge_core directly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bridge_core.config import BridgeConfig
from bridge_core.data_engine import DataEngine

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

if __name__ == "__main__":
    engine = DataEngine()
    try:
        asyncio.run(engine.run())
    except KeyboardInterrupt:
        engine.stop()
        print("\n👋 Bridge encerrado.")
