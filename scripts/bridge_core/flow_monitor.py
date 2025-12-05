import json
import os
import time
import logging
from datetime import datetime
from .config import BridgeConfig

logger = logging.getLogger("Bridge.FlowMonitor")

class FlowMonitor:
    def __init__(self):
        # Path to MT5 Common Files
        self.common_path = os.path.join(os.getenv("APPDATA"), "MetaQuotes", "Terminal", "Common", "Files")
        self.last_mtime = 0
        self.current_flow = {
            "FOREIGN": 0,
            "INSTITUTIONAL": 0,
            "RETAIL": 0
        }
        
    def check_update(self):
        """
        Checks if any flow_data_*.json file has been updated and reads it.
        Prioritizes WIN$N or WIN$.
        """
        try:
            if not os.path.exists(self.common_path):
                return None
            
            # Find the most relevant file (WIN$N or WIN$)
            target_file = None
            for filename in os.listdir(self.common_path):
                if filename.startswith("flow_data_") and filename.endswith(".json"):
                    if "WIN" in filename: # Prioritize WIN
                        target_file = os.path.join(self.common_path, filename)
                        break
            
            if not target_file:
                return None
                
            mtime = os.path.getmtime(target_file)
            if mtime > self.last_mtime:
                self.last_mtime = mtime
                
                # Retry loop for file locking issues
                for _ in range(3):
                    try:
                        with open(target_file, 'r') as f:
                            data = json.load(f)
                            if "flow" in data:
                                self.current_flow = data["flow"]
                                return self.current_flow
                    except json.JSONDecodeError:
                        time.sleep(0.1) # Wait for write to complete
                    except PermissionError:
                        time.sleep(0.1) # Wait for lock release
                        
        except Exception as e:
            logger.error(f"❌ Error reading flow data: {e}")
            
        return None

    def calculate_quant_score(self, flow_data, macro_data, technical_data):
        """
        Calculates the Quant Score (0-15) based on multiple factors.
        """
        score = 0
        details = []
        
        # 1. Flow Rules (Max 5 pts)
        gringo_vol = flow_data.get("FOREIGN", 0)
        if gringo_vol > 500: 
            score += 2
            details.append("Gringo Comprado (+2)")
        elif gringo_vol < -500:
            score += 0 # Bearish doesn't add to "Buy Score" in this logic, or we can make it signed.
            # Assuming Score 0-15 is "Bullish Strength". For Bearish, we might need a different scale.
            # Let's assume the user wants a "Bullish Score".
            details.append("Gringo Vendido (0)")
        
        inst_vol = flow_data.get("INSTITUTIONAL", 0)
        if inst_vol > 500:
            score += 1
            details.append("Institucional Comprado (+1)")
            
        # 2. Macro Rules (Max 5 pts)
        sp500 = macro_data.get("SP500", {}).get("var_pct", 0)
        if sp500 > 0.1:
            score += 2
            details.append("S&P 500 Alta (+2)")
            
        dxy = macro_data.get("DXY", {}).get("var_pct", 0)
        if dxy < -0.1:
            score += 1
            details.append("Dólar Global Caindo (+1)")
            
        # 3. Technical Rules (Max 5 pts)
        # Example: Price > VWAP (Need VWAP from MT5 or calc)
        # Placeholder logic
        
        return {
            "score": score,
            "max_score": 15,
            "details": details,
            "sentiment": "BULLISH" if score >= 7 else "NEUTRAL/BEARISH"
        }
