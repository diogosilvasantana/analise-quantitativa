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

    def _calculate_single_score(self, flow, macro_data, blue_chips, asset_type):
        """Helper to calculate score for a single asset."""
        bull_power = 0
        bear_power = 0
        details = []
        
        # --- 1. Flow Analysis (Weight: 50%) ---
        # Normalize flow: 5000 contracts = 100% power contribution
        MAX_FLOW_REF = 5000 
        
        # Foreigners (Gringo) - Weight 25
        gringo_vol = flow.get("FOREIGN", 0)
        gringo_score = min(abs(gringo_vol) / MAX_FLOW_REF, 1.0) * 25
        if gringo_vol > 0:
            bull_power += gringo_score
            if gringo_vol > 1000: details.append(f"Gringo Comprado ({int(gringo_score)})")
        else:
            bear_power += gringo_score
            if gringo_vol < -1000: details.append(f"Gringo Vendido ({int(gringo_score)})")

        # Institutional - Weight 15
        inst_vol = flow.get("INSTITUTIONAL", 0)
        inst_score = min(abs(inst_vol) / MAX_FLOW_REF, 1.0) * 15
        if inst_vol > 0:
            bull_power += inst_score
            if inst_vol > 1000: details.append(f"Inst. Comprado ({int(inst_score)})")
        else:
            bear_power += inst_score
            if inst_vol < -1000: details.append(f"Inst. Vendido ({int(inst_score)})")
            
        # Retail - Weight 10
        retail_vol = flow.get("RETAIL", 0)
        retail_score = min(abs(retail_vol) / MAX_FLOW_REF, 1.0) * 10
        if retail_vol > 0:
            bull_power += retail_score
        else:
            bear_power += retail_score

        # --- 2. Macro Analysis (Weight: 20%) ---
        # SP500 and DXY
        sp500 = macro_data.get("SP500", {}).get("var_pct", 0)
        dxy = macro_data.get("DXY", {}).get("var_pct", 0)
        
        macro_bull = 0
        macro_bear = 0
        
        if asset_type == "WIN":
            if sp500 > 0.1: macro_bull += 10; details.append("S&P 500 Alta")
            elif sp500 < -0.1: macro_bear += 10; details.append("S&P 500 Queda")
            
            if dxy < -0.1: macro_bull += 10; details.append("DXY Queda")
            elif dxy > 0.1: macro_bear += 10; details.append("DXY Alta")
            
        elif asset_type == "WDO":
            if dxy > 0.1: macro_bull += 10; details.append("DXY Alta")
            elif dxy < -0.1: macro_bear += 10; details.append("DXY Queda")
            
            if sp500 < -0.1: macro_bull += 10; details.append("S&P 500 Queda")
            elif sp500 > 0.1: macro_bear += 10; details.append("S&P 500 Alta")

        bull_power += macro_bull
        bear_power += macro_bear
        
        # --- 3. IBOV Top 10 Analysis (Weight: 30%) ---
        # Only for WIN. For WDO, we invert the logic (IBOV down -> WDO up usually)
        if blue_chips:
            positive_stocks = sum(1 for s in blue_chips.values() if s.get('change_pct', 0) > 0)
            negative_stocks = sum(1 for s in blue_chips.values() if s.get('change_pct', 0) < 0)
            total_stocks = len(blue_chips)
            
            if total_stocks > 0:
                # Calculate net sentiment (-1 to +1)
                ibov_sentiment = (positive_stocks - negative_stocks) / total_stocks
                ibov_score = abs(ibov_sentiment) * 30 # Max 30 points
                
                if asset_type == "WIN":
                    if ibov_sentiment > 0.2: # Mostly positive
                        bull_power += ibov_score
                        details.append(f"Blue Chips Alta ({int(ibov_score)})")
                    elif ibov_sentiment < -0.2: # Mostly negative
                        bear_power += ibov_score
                        details.append(f"Blue Chips Queda ({int(ibov_score)})")
                elif asset_type == "WDO":
                    # Inverse correlation
                    if ibov_sentiment < -0.2: # IBOV down -> WDO up
                        bull_power += ibov_score
                        details.append(f"Blue Chips Queda ({int(ibov_score)})")
                    elif ibov_sentiment > 0.2: # IBOV up -> WDO down
                        bear_power += ibov_score
                        details.append(f"Blue Chips Alta ({int(ibov_score)})")

        # --- 4. Divergence Penalty (Safety Check) ---
        # If Bull Power is high (Flow) but Bear Power is significant (Price/Macro),
        # we must reduce the Bull Score to avoid "Strong Buy" in a crash.
        
        if bull_power > 60 and bear_power > 30:
            penalty = bear_power * 0.5
            bull_power -= penalty
            details.append(f"Penalidade Divergência (-{int(penalty)})")
            
        # Cap at 100
        bull_power = min(max(bull_power, 0), 100)
        bear_power = min(max(bear_power, 0), 100)
        
        # Calculate Net Score (0-15 scale)
        net_raw = bull_power - bear_power
        
        # Improved Scaling: Center at 7.5 (Neutral)
        # Range -100 to +100 maps to 0 to 15
        # -100 -> 0
        # 0 -> 7.5
        # +100 -> 15
        score_scaled = ((net_raw + 100) / 200) * 15
        
        return {
            "score": round(score_scaled, 1),
            "bull_power": int(bull_power),
            "bear_power": int(bear_power),
            "max_score": 15,
            "details": details,
            "sentiment": "BULLISH" if bull_power > bear_power else "BEARISH"
        }

    def calculate_quant_score(self, flows, macro_data, blue_chips):
        """
        Calculates the Quant Score (0-15) for both WIN and WDO.
        """
        win_flow = flows.get("WIN", {})
        wdo_flow = flows.get("WDO", {})
        
        return {
            "WIN": self._calculate_single_score(win_flow, macro_data, blue_chips, "WIN"),
            "WDO": self._calculate_single_score(wdo_flow, macro_data, blue_chips, "WDO")
        }
