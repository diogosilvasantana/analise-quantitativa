import time
import schedule
import logging
import sys
import os

# Add 'ai-analyst' directory to path to allow relative imports if run from root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from collector import DataCollector
from analyzer import MarketAnalyzer
from notifier import Notifier
from config import Config

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("AIAnalyst.Main")

def job():
    logger.info("⏰ Starting Daily AI Analysis Job...")
    
    try:
        # 1. Collect Data
        collector = DataCollector()
        data = collector.collect_all()
        logger.info("✅ Data Collection Complete.")
        
        # 2. Analyze with AI
        analyzer = MarketAnalyzer()
        analysis = analyzer.analyze_market(data)
        if "error" in analysis:
            logger.error(f"❌ Analysis Failed: {analysis['error']}")
            return
        
        logger.info("✅ AI Analysis Complete.")
        logger.info(f"📊 Sentiment: {analysis.get('sentiment')} ({analysis.get('confidence')}%)")
        
        # 3. Notify
        notifier = Notifier()
        notifier.send_report(analysis)
        logger.info("✅ Report Distributed.")
        
    except Exception as e:
        logger.error(f"❌ Job Failed: {e}")

if __name__ == "__main__":
    logger.info(f"🚀 AI Analyst Service Started. Scheduled for {Config.SCHEDULE_TIME}...")
    
    # Schedule the job
    schedule.every().day.at(Config.SCHEDULE_TIME).do(job)
    
    # Run once immediately for testing/debug (Optional - remove in production)
    # logger.info("🧪 Running immediate test...")
    job()
    
    while True:
        schedule.run_pending()
        time.sleep(60)
