import requests
import feedparser
import logging
from datetime import datetime, timedelta
from config import Config

logger = logging.getLogger("AIAnalyst.Collector")

class DataCollector:
    def __init__(self):
        self.backend_url = Config.BACKEND_URL
        
    def get_dashboard_data(self):
        """Fetches current market snapshot from Backend with retries."""
        max_retries = 5
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                response = requests.get(f"{self.backend_url}/api/dashboard_data", timeout=10)
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Failed to fetch dashboard data (Attempt {attempt+1}/{max_retries}): {response.status_code}")
            except Exception as e:
                logger.warning(f"Connection error fetching dashboard data (Attempt {attempt+1}/{max_retries}): {e}")
            
            if attempt < max_retries - 1:
                import time
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
        
        logger.error("❌ Could not connect to Backend after multiple attempts.")
        return {}

    def get_history_data(self, asset: str):
        """Fetches historical data (D1/H1) for an asset with retries."""
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                # Fetch D1 by default for context
                response = requests.get(f"{self.backend_url}/api/history/{asset}", params={"timeframe": "D1"}, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if "error" not in data:
                        return data
                
                logger.warning(f"History endpoint returned error for {asset}: {response.text}")
                return [] # Don't retry if it's a 404/500 from app logic, only connection errors
            except Exception as e:
                logger.warning(f"Connection error fetching history for {asset} (Attempt {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    import time
                    time.sleep(retry_delay)
        
        return []

    def get_news_headlines(self):
        """Fetches headlines from RSS feeds."""
        headlines = []
        for feed_url in Config.RSS_FEEDS:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:5]: # Top 5 per feed
                    headlines.append({
                        "title": entry.title,
                        "link": entry.link,
                        "published": entry.published if 'published' in entry else datetime.now().isoformat()
                    })
            except Exception as e:
                logger.error(f"Error parsing feed {feed_url}: {e}")
        return headlines

    def collect_all(self):
        """Aggregates all data for the analyst."""
        logger.info("Collecting data...")
        
        dashboard = self.get_dashboard_data()
        
        # Collect history for key assets
        win_history = self.get_history_data("WIN$N") # Current contract
        wdo_history = self.get_history_data("WDO$N")
        
        news = self.get_news_headlines()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "dashboard": dashboard,
            "technical_context": {
                "WIN": win_history,
                "WDO": wdo_history
            },
            "news": news
        }
