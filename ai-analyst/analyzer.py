import logging
import json
import anthropic
from config import Config

logger = logging.getLogger("AIAnalyst.Analyzer")

class MarketAnalyzer:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)

    def analyze_market(self, data: dict) -> dict:
        """
        Generates a quantitative pre-market report using Claude 3.5 Sonnet.
        """
        logger.info("Generating analysis with Claude...")
        
        # Prepare context
        dashboard = data.get("dashboard", {})
        tech_context = data.get("technical_context", {})
        news = data.get("news", [])
        
        # Helper to safely get nested data
        def get_val(source, path, default=0.0):
            try:
                val = source
                for key in path:
                    val = val.get(key, {})
                return val if isinstance(val, (int, float)) else default
            except:
                return default

        # Extract specific data points for the prompt
        brent_change = get_val(dashboard, ['commodities', 'BRENT', 'var_pct'])
        iron_ore_change = get_val(dashboard, ['commodities', 'MINERIO_FERRO', 'var_pct'])
        sp500_change = get_val(dashboard, ['indices_globais', 'SP500', 'var_pct'])
        dxy_change = get_val(dashboard, ['indices_globais', 'DXY', 'var_pct'])
        
        # New Ingredients (ADRs & EWZ)
        ewz_change = get_val(dashboard, ['indices_globais', 'EWZ', 'var_pct'])
        pbr_change = get_val(dashboard, ['indices_globais', 'PBR', 'var_pct'])
        vale_adr_change = get_val(dashboard, ['indices_globais', 'VALE_ADR', 'var_pct'])
        
        # New Ingredients (DIs & Adjustment)
        di27_change = get_val(dashboard, ['taxas', 'DI_MT5', 'var_pct'])
        di29_change = get_val(dashboard, ['taxas', 'DI1F29', 'var_pct'])
        
        win_ajuste = get_val(dashboard, ['win', 'ajuste'])
        wdo_ajuste = get_val(dashboard, ['wdo', 'ajuste'])
        
        # Calendar (Already filtered by Bridge for High Impact)
        calendar = dashboard.get('calendar', [])
        
        # Extract Technicals (Assuming list of dicts, last item is most recent)
        win_data = tech_context.get('WIN', [])
        wdo_data = tech_context.get('WDO', [])
        
        win_close = win_data[-1].get('close') if win_data else 0
        wdo_close = wdo_data[-1].get('close') if wdo_data else 0
        
        # Simple Trend Logic (Last close > Close 20 days ago) - Placeholder
        trend_d1 = "NEUTRO"
        if len(win_data) > 20:
            trend_d1 = "ALTA" if win_close > win_data[-20].get('close') else "BAIXA"

        SYSTEM_PROMPT = """
        Você é um Estrategista de Mercado Sênior (Market Profile & Price Action).
        Sua função NÃO é dar call de compra/venda.
        Sua função é desenhar o CENÁRIO PROVÁVEL e o COMPORTAMENTO esperado para WIN e WDO.
        Analise a estrutura de mercado (Tendência, Suportes, Resistências) cruzada com o Macro.
        
        CRÍTICO:
        1. Use EXATAMENTE os preços de fechamento fornecidos (WIN Fechamento, WDO Fechamento) como referência.
        2. Se o preço for 0 ou desconhecido, use "AGUARDANDO DADOS".
        3. Responda estritamente com o JSON solicitado.
        """

        USER_PROMPT = f"""
        DADOS DE ENTRADA (FACTUAL):
        
        1. **O "Oráculo" (Pré-Market NY):**
           - EWZ (Brasil ETF): {ewz_change}%
           - Petrobras ADR: {pbr_change}%
           - Vale ADR: {vale_adr_change}%
           - S&P 500 Futuro: {sp500_change}%
           - DXY (Dólar Global): {dxy_change}%
           
        2. **Commodities:**
           - Petróleo Brent: {brent_change}%
           - Minério de Ferro (Dalian): {iron_ore_change}%
           
        3. **Estrutura B3 (O "Rastro do Dinheiro"):**
           - WIN Ajuste (Imã): {win_ajuste}
           - WDO Ajuste (Imã): {wdo_ajuste}
           - Juros DI1F27: {di27_change}%
           - Juros DI1F29: {di29_change}%
           
        4. **Técnico (Ontem):**
           - WIN Fechamento: {win_close}
           - WDO Fechamento: {wdo_close}
           - Tendência D1: {trend_d1}
           
        5. **Campo Minado (Calendário Econômico):**
           {json.dumps(calendar, indent=2)}
           
        6. **Notícias Relevantes:**
           {json.dumps(news, indent=2)}

        ---

        GERE UMA ANÁLISE DE CONTEXTO (JSON) COM A SEGUINTE ESTRUTURA:

        1. **NARRATIVA DO DIA (O "Storytelling"):**
           - Explique o que o mercado vai tentar fazer hoje.
           - Ex: "O Índice deve tentar renovar a máxima de ontem impulsionado pelo S&P, mas pode encontrar barreira nos 130k."
           - Ex: "O Dólar tende a buscar a VWAP mensal para corrigir a alta exagerada de ontem."

        2. **COMPORTAMENTO ESPERADO (WIN):**
           - **Viés:** (Alta / Baixa / Lateral / Consolidação).
           - **Objetivos (Ímãs):** Quais pontos o preço vai buscar? (Ex: Máxima de ontem, Ajuste, Média de 200).
           - **Estrutura:** Está em tendência clara ou range?
           - **Alerta:** (Ex: "Cuidado com rompimentos falsos na abertura devido à baixa liquidez").

        3. **COMPORTAMENTO ESPERADO (WDO):**
           - **Viés:** (Alta / Baixa / Lateral).
           - **Objetivos:** Pontos de atração (Ex: Mínima de ontem, 5.500).
           - **Recomendação de Postura:** (Ex: "Dia travado, evite operar meio de gráfico. Opere apenas extremos").

        4. **PONTOS DE DECISÃO (Suporte/Resistência):**
           - Liste 3 Suportes e 3 Resistências chaves para cada ativo.
           - Explique O PORQUÊ de cada ponto (Ex: "128.500 - Ajuste de ontem").

        5. **RESUMO EXECUTIVO:**
           - Uma frase final para o trader colar no monitor. (Ex: "Foco na compra de Índice acima do Ajuste; Dólar lateral, operar apenas nas pontas").

        6. **ANÁLISE DE FLUXO (Players):**
           - Baseado no cenário Macro (Risk On/Off), qual deve ser a postura dos **Estrangeiros** hoje? (Compradores ou Vendedores?)
           - Como os **Institucionais** devem reagir aos níveis de preço atuais? (Devem defender suporte ou realizar lucro?)
           - Onde a **Pessoa Física** pode ser estopada? (Pontos de dor/liquidez).

        FORMATO JSON ESPERADO:
        {{
          "narrative": "...",
          "win_context": {{ "bias": "...", "magnets": ["..."], "structure": "...", "alert": "..." }},
          "wdo_context": {{ "bias": "...", "magnets": ["..."], "structure": "...", "alert": "..." }},
          "key_levels": {{ "win": {{ "supports": [], "resistances": [] }}, "wdo": {{ "supports": [], "resistances": [] }} }},
          "executive_summary": "...",
          "players_outlook": {{
               "foreigners": "...",
               "institutions": "...",
               "retail_risk": "..."
           }}
        }}
        """

        try:
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4000,
                temperature=0.1, # Reduced temperature for more objective/quantitative results
                system=SYSTEM_PROMPT,
                messages=[
                    {"role": "user", "content": USER_PROMPT}
                ]
            )
            
            # Extract JSON from response
            content = message.content[0].text
            # Simple cleanup if markdown code blocks are used
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
                
            return json.loads(content)

        except Exception as e:
            logger.error(f"Error calling Claude API: {e}")
            return {"error": str(e)}
