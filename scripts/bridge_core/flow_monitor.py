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
    
    def _is_market_open(self):
        """Check if Brazilian market is currently open."""
        now = datetime.now()
        
        # Weekend
        if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False
        
        # Market hours: 9:00 - 18:00 (BRT)
        if now.hour < 9 or now.hour >= 18:
            return False
        
        return True
    
    def _calculate_bull_bear_from_variation(self, variation_pct):
        """
        Calculate Bull/Bear Power from daily variation when market is closed.
        
        Args:
            variation_pct: Daily variation percentage (e.g., -0.5 for -0.5%)
        
        Returns:
            tuple: (bull_power, bear_power)
        """
        max_power = 15
        
        if variation_pct > 0:
            # Positive variation = Bull market
            # Scale: 0.5% = 5 pts, 1% = 10 pts, 2%+ = 15 pts
            bull_power = min(abs(variation_pct) * 10, max_power)
            bear_power = 0
        elif variation_pct < 0:
            # Negative variation = Bear market
            bull_power = 0
            bear_power = min(abs(variation_pct) * 10, max_power)
        else:
            # No variation = Neutral
            bull_power = 7.5
            bear_power = 7.5
        
        return bull_power, bear_power
        
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

    def _calculate_single_score(self, flow, macro_data, blue_chips, asset_type, mt5_client=None):
        """
        Calculates Quant Score (0-15) using Quant Trader Original strategy.
        
        Weights:
        - Fluxo de Players: 9 pts (Gringo 6, Inst 3, Varejo 0)
        - Macro & Correlações: 3 pts
        - Ativo Específico: 3 pts
        """
        bull_power = 0
        bear_power = 0
        details = []
        
        # --- CHECK IF MARKET IS CLOSED ---
        market_open = self._is_market_open()
        
        if not market_open:
            # Market is closed - use daily variation instead
            symbol_key = "WIN$N" if asset_type == "WIN" else "WDO$N"
            asset_data = macro_data.get(symbol_key, {})
            variation_pct = asset_data.get("var_pct", 0)
            
            # Calculate Bull/Bear from variation
            bull_power, bear_power = self._calculate_bull_bear_from_variation(variation_pct)
            
            # Add market closed indicator
            if variation_pct > 0:
                details.append(f"🔒 Mercado Fechado (Var: +{variation_pct:.2f}%)")
                status = "AGUARDAR"
                sentiment = "NEUTRAL"
            elif variation_pct < 0:
                details.append(f"🔒 Mercado Fechado (Var: {variation_pct:.2f}%)")
                status = "AGUARDAR"
                sentiment = "NEUTRAL"
            else:
                details.append("🔒 Mercado Fechado (Sem Variação)")
                status = "AGUARDAR"
                sentiment = "NEUTRAL"
            
            return {
                "score": 0,  # No score when market is closed
                "bull_power": round(bull_power, 1),
                "bear_power": round(bear_power, 1),
                "max_score": 15,
                "details": details,
                "sentiment": sentiment,
                "status": status,
                "direction": "NONE",
                "market_status": "CLOSED"
            }
        
        # Market is OPEN - proceed with normal calculation
        details.append("✅ Mercado Aberto")
        
        # --- 1. Fluxo de Players (9 pontos) ---
        # Normalização por Média Móvel de Volume (10 dias)
        
        # Get volume average (fallback to 5000 if MT5 not available)
        avg_volume = 5000
        if mt5_client:
            try:
                avg_volume = mt5_client.get_volume_average(
                    "WIN$N" if asset_type == "WIN" else "WDO$N", 
                    days=10
                )
            except Exception as e:
                logger.warning(f"⚠️ Erro ao obter volume médio: {e}")
        
        # Estrangeiro (Gringo) - Weight 6 pts (DRIVER PRINCIPAL)
        gringo_vol = flow.get("FOREIGN", 0)
        gringo_normalized = min(abs(gringo_vol) / avg_volume, 1.0)
        gringo_score = gringo_normalized * 6
        
        if gringo_vol > 0:
            bull_power += gringo_score
            if gringo_vol > avg_volume * 0.3:  # Significativo (>30% da média)
                details.append(f"🌍 Gringo Comprador ({int(gringo_score)})")
        else:
            bear_power += gringo_score
            if gringo_vol < -avg_volume * 0.3:
                details.append(f"🌍 Gringo Vendedor ({int(gringo_score)})")

        # Institucional - Weight 3 pts (APOIO SECUNDÁRIO)
        inst_vol = flow.get("INSTITUTIONAL", 0)
        inst_normalized = min(abs(inst_vol) / avg_volume, 1.0)
        inst_score = inst_normalized * 3
        
        if inst_vol > 0:
            bull_power += inst_score
            if inst_vol > avg_volume * 0.3:
                details.append(f"🏦 Inst. Comprador ({int(inst_score)})")
        else:
            bear_power += inst_score
            if inst_vol < -avg_volume * 0.3:
                details.append(f"🏦 Inst. Vendedor ({int(inst_score)})")
            
        # Varejo - Weight 0 pts (APENAS INFORMATIVO)
        retail_vol = flow.get("RETAIL", 0)
        # Não soma no score, mas registra para informação
        if abs(retail_vol) > avg_volume * 0.2:
            retail_dir = "Comprador" if retail_vol > 0 else "Vendedor"
            details.append(f"👥 Varejo {retail_dir} (Info)")

        # --- 2. Macro & Correlações (3 pontos) ---
        
        macro_bull = 0
        macro_bear = 0
        
        if asset_type == "WIN":
            # WIN: Correlação Inversa (Dólar e Juros caindo = Índice subindo)
            
            # Dólar Futuro (WDO) - 1.5 pts
            wdo_var = macro_data.get("WDO$N", {}).get("var_pct", 0)
            if wdo_var < -0.1:  # Dólar caindo
                macro_bull += 1.5
                details.append("💵 Dólar Caindo")
            elif wdo_var > 0.1:  # Dólar subindo
                macro_bear += 1.5
                details.append("💵 Dólar Subindo")
            
            # Juros Futuros (DI) - 1.5 pts
            di_var = macro_data.get("DI_MT5", {}).get("var_pct", 0)
            if di_var < -0.05:  # Juros caindo
                macro_bull += 1.5
                details.append("📉 Juros Caindo")
            elif di_var > 0.05:  # Juros subindo
                macro_bear += 1.5
                details.append("📈 Juros Subindo")
                
        elif asset_type == "WDO":
            # WDO: Correlação Direta (DXY e Juros subindo = Dólar subindo)
            
            # DXY - 1.5 pts
            dxy_var = macro_data.get("DXY", {}).get("var_pct", 0)
            if dxy_var > 0.1:  # DXY subindo
                macro_bull += 1.5
                details.append("💲 DXY Subindo")
            elif dxy_var < -0.1:  # DXY caindo
                macro_bear += 1.5
                details.append("💲 DXY Caindo")
            
            # Juros Futuros (DI) - 1.5 pts
            di_var = macro_data.get("DI_MT5", {}).get("var_pct", 0)
            if di_var > 0.05:  # Juros subindo
                macro_bull += 1.5
                details.append("📈 Juros Subindo")
            elif di_var < -0.05:  # Juros caindo
                macro_bear += 1.5
                details.append("📉 Juros Caindo")

        bull_power += macro_bull
        bear_power += macro_bear
        
        # --- 3. Ativo Específico (3 pontos) ---
        
        if asset_type == "WIN":
            # WIN: Top 10 Ações (EXCLUSIVO)
            
            # Filtro de Horário (antes das 10:00 AM)
            from datetime import datetime
            current_hour = datetime.now().hour
            
            if current_hour < 10:
                details.append("⏰ Aguardando Abertura à Vista (10:00)")
            elif blue_chips:
                positive_stocks = sum(1 for s in blue_chips.values() if s.get('var_pct', 0) > 0)
                negative_stocks = sum(1 for s in blue_chips.values() if s.get('var_pct', 0) < 0)
                total_stocks = len(blue_chips)
                
                if total_stocks > 0:
                    # Sentimento: -1 (todas caindo) a +1 (todas subindo)
                    ibov_sentiment = (positive_stocks - negative_stocks) / total_stocks
                    ibov_score = abs(ibov_sentiment) * 3  # Máximo 3 pontos
                    
                    if ibov_sentiment > 0.2:  # Maioria subindo (>60%)
                        bull_power += ibov_score
                        details.append(f"📊 Top 10 Alta ({int(ibov_score)})")
                    elif ibov_sentiment < -0.2:  # Maioria caindo (<40%)
                        bear_power += ibov_score
                        details.append(f"📊 Top 10 Queda ({int(ibov_score)})")
                        
        elif asset_type == "WDO":
            # WDO: VWAP + Ajuste (EXCLUSIVO)
            
            vwap_score = 0
            
            # Get current price and ajuste
            wdo_data = macro_data.get("WDO$N", {})
            current_price = wdo_data.get("valor", 0)
            ajuste = wdo_data.get("ajuste", 0)
            
            # Calculate VWAP if MT5 available
            vwap = None
            if mt5_client:
                try:
                    vwap = mt5_client.calculate_vwap("WDO$N", period_minutes=60)
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao calcular VWAP: {e}")
            
            # VWAP Analysis (1.5 pts)
            if vwap and current_price > 0:
                dist_vwap = ((current_price - vwap) / vwap) * 100
                
                if dist_vwap > 0.1:  # Acima de VWAP
                    vwap_score += 1.5
                    details.append("📈 Acima VWAP")
                elif dist_vwap < -0.1:  # Abaixo de VWAP
                    vwap_score -= 1.5
                    details.append("📉 Abaixo VWAP")
            
            # Ajuste Analysis (1.5 pts)
            if ajuste > 0 and current_price > 0:
                dist_ajuste = ((current_price - ajuste) / ajuste) * 100
                
                if dist_ajuste > 0.1:  # Acima de Ajuste
                    vwap_score += 1.5
                    details.append("📈 Acima Ajuste")
                elif dist_ajuste < -0.1:  # Abaixo de Ajuste
                    vwap_score -= 1.5
                    details.append("📉 Abaixo Ajuste")
            
            # Apply score
            if vwap_score > 0:
                bull_power += abs(vwap_score)
            else:
                bear_power += abs(vwap_score)


        # --- 4. Filtro de Divergência Crítica ---
        # Se Score alto mas Gringo contra = ALERTA
        
        # Cap at 15
        bull_power = min(max(bull_power, 0), 15)
        bear_power = min(max(bear_power, 0), 15)
        
        # --- 5. Decision Logic (ABSOLUTE SCORES) ---
        # FIX: Use absolute scores, not centered normalization
        # Old (WRONG): score = ((bull - bear + 15) / 30) * 15
        #   Problem: When bull=0, bear=0 → score = 7.5 (AUTORIZADO incorrectly!)
        # New (CORRECT): Compare absolute scores
        
        bull_score = bull_power  # 0-15
        bear_score = bear_power  # 0-15
        
        # Determine direction and status
        if bull_score >= 7 and bull_score > bear_score:
            status = "COMPRA AUTORIZADA"
            sentiment = "BULLISH"
            dominant_score = bull_score
        elif bear_score >= 7 and bear_score > bull_score:
            status = "VENDA AUTORIZADA"
            sentiment = "BEARISH"
            dominant_score = bear_score
        else:
            status = "AGUARDAR"
            sentiment = "NEUTRAL"
            dominant_score = max(bull_score, bear_score)
        
        # Check for critical divergence override
        if bull_score >= 12 and gringo_vol < -avg_volume * 0.2:
            status = "DIVERGÊNCIA CRÍTICA"
            sentiment = "WARNING"
            details.append("⚠️ DIVERGÊNCIA: Score Alto + Gringo Vendedor!")
        
        return {
            "score": round(dominant_score, 1),  # Dominant score (0-15)
            "bull_power": int(bull_power),
            "bear_power": int(bear_power),
            "max_score": 15,
            "details": details,
            "sentiment": sentiment,
            "status": status,  # COMPRA AUTORIZADA / VENDA AUTORIZADA / AGUARDAR / DIVERGÊNCIA
            "direction": "BUY" if sentiment == "BULLISH" else ("SELL" if sentiment == "BEARISH" else "NEUTRAL"),
            "market_status": "OPEN"
        }

    def calculate_quant_score(self, flows, macro_data, blue_chips, mt5_client=None):
        """
        Calculates the Quant Score (0-15) for both WIN and WDO.
        
        Args:
            flows: Flow data for WIN and WDO
            macro_data: Macro indicators (DI, DXY, etc.)
            blue_chips: Top 10 IBOV stocks data
            mt5_client: MT5Client instance for VWAP and volume calculations
        """
        win_flow = flows.get("WIN", {})
        wdo_flow = flows.get("WDO", {})
        
        return {
            "WIN": self._calculate_single_score(win_flow, macro_data, blue_chips, "WIN", mt5_client),
            "WDO": self._calculate_single_score(wdo_flow, macro_data, blue_chips, "WDO", mt5_client)
        }
