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
        self.last_mtime = {} # Track mtime per file
        self.current_flows = {} # Store flow per asset
        
    def check_update(self):
        """
        Checks if any flow_data_*.json file has been updated.
        Returns a dict: {"WIN": {...}, "WDO": {...}}
        """
        try:
            if not os.path.exists(self.common_path):
                return self.current_flows
            
            updated = False
            
            for filename in os.listdir(self.common_path):
                if filename.startswith("flow_data_") and filename.endswith(".json"):
                    file_path = os.path.join(self.common_path, filename)
                    
                    # Determine Asset Type
                    asset_type = "UNKNOWN"
                    if "WIN" in filename: asset_type = "WIN"
                    elif "WDO" in filename: asset_type = "WDO"
                    else: continue
                    
                    mtime = os.path.getmtime(file_path)
                    
                    # Check if file is new or updated
                    if file_path not in self.last_mtime or mtime > self.last_mtime[file_path]:
                        self.last_mtime[file_path] = mtime
                        
                        # Read File
                        for _ in range(3):
                            try:
                                with open(file_path, 'r') as f:
                                    data = json.load(f)
                                    if "flow" in data:
                                        self.current_flows[asset_type] = data["flow"]
                                        updated = True
                                break
                            except (json.JSONDecodeError, PermissionError):
                                time.sleep(0.05)
                                
            if updated:
                return self.current_flows
            
            return None # No updates
                        
        except Exception as e:
            logger.error(f"❌ Error reading flow data: {e}")
            return None

    def _calculate_single_score(self, flow, macro_data, asset_type):
        """Helper to calculate score for a single asset."""
        score = 0
        details = []
        
        # 1. Flow Rules (Max 5 pts)
        gringo_vol = flow.get("FOREIGN", 0)
        if gringo_vol > 500: 
            score += 2
            details.append("Gringo Comprado (+2)")
        elif gringo_vol < -500:
            # For WDO, Gringo Sold might be Bullish for Real (Bearish for Dollar)
            # But let's keep it simple: Score is "Bullish Strength for the Asset"
            # So Gringo Sold = Bearish for Asset = 0 pts (or negative if we had that scale)
            details.append("Gringo Vendido (0)")
        
        inst_vol = flow.get("INSTITUTIONAL", 0)
        if inst_vol > 500:
            score += 1
            details.append("Institucional Comprado (+1)")

        # 2. Macro Rules (Max 5 pts)
        # Different rules for WIN vs WDO
        sp500 = macro_data.get("SP500", {}).get("var_pct", 0)
        dxy = macro_data.get("DXY", {}).get("var_pct", 0)

        if asset_type == "WIN":
            if sp500 > 0.1: score += 2; details.append("S&P 500 Alta (+2)")
            if dxy < -0.1: score += 1; details.append("DXY Queda (+1)")
        elif asset_type == "WDO":
            if dxy > 0.1: score += 2; details.append("DXY Alta (+2)")
            if sp500 < -0.1: score += 1; details.append("S&P 500 Queda (+1)")

        return {
            "score": score,
            "max_score": 15,
            "details": details,
            "sentiment": "BULLISH" if score >= 7 else "NEUTRAL/BEARISH"
        }

    def calculate_quant_score(self, flows, macro_data, technical_data):
        """
        Calculates the Quant Score (0-15) for both WIN and WDO.
        """
        win_flow = flows.get("WIN", {})
        wdo_flow = flows.get("WDO", {})
        
        return {
            "WIN": self._calculate_single_score(win_flow, macro_data, "WIN"),
            "WDO": self._calculate_single_score(wdo_flow, macro_data, "WDO")
        }
