# Profit Pro RTD Bridge - Setup Guide

## Instalação

### 1. Instalar Dependências

```bash
pip install xlwings
```

**Nota**: `xlwings` requer que o Excel esteja instalado no Windows.

---

## Configuração do Excel

### 1. Criar Arquivo `profit-data.xlsx`

Crie um arquivo Excel na **raiz do projeto** com o nome `profit-data.xlsx`.

### 2. Estrutura da Planilha

**Aba**: "Dados"

**Layout**:

| Coluna | Descrição |
|--------|-----------|
| A | Timestamp |
| B | Preço Atual |
| G | Bear Power |
| H | Bull Power |
| I | Hilo Activator |
| J | IFR (RSI) |
| L | Fluxo (Trade Radar) |
| M | VWAP |
| Q | Score Quant |
| R | Decisão Final |

**Linhas**:
- Linha 2: WIN (Mini Índice)
- Linha 3: WDO (Mini Dólar)
- Linha 16: S&P 500 Variação (célula E16)
- Linha 17: DI Variação (célula E17)

### 3. Configurar RTD no Profit Pro

No Profit Pro:
1. Vá em `Ferramentas` → `RTD`
2. Configure os campos para exportar para as células corretas
3. Exemplo de fórmula RTD:
   ```excel
   =RTD("ProfitPro.RTD",,"WIN$","LAST")
   ```

---

## Uso

### Teste Standalone

```bash
cd e:\projetos\ai-trader-pro\scripts\bridge_core
python profit_bridge.py
```

**Saída esperada**:
```
============================================================
Profit Pro RTD Bridge - Test Mode
============================================================

Make sure 'profit-data.xlsx' is OPEN in Excel!
Press Ctrl+C to stop

============================================================
Timestamp: 2025-12-06 01:40:00

------------------------------------------------------------

📊 WIN (Mini Índice)
   Preço: 129500.00
   Bull Power: 8.5 | Bear Power: 2.3
   RSI: 62.4 | VWAP: 129450.00
   Fluxo: 2500.0
   Score: 11.2 | Decisão: COMPRA AUTORIZADA

💵 WDO (Mini Dólar)
   Preço: 5650.00
   Bull Power: 6.1 | Bear Power: 4.2
   RSI: 55.3 | VWAP: 5645.00
   Fluxo: -800.0
   Score: 7.8 | Decisão: COMPRA AUTORIZADA

🌍 Macro
   DI Var: -0.08%
   S&P 500 Var: 0.25%
```

### Integração com DataEngine

```python
from bridge_core.profit_bridge import ProfitBridge

# Inicializar
profit = ProfitBridge("profit-data.xlsx")

# Ler dados
data = profit.get_data()

# Acessar
win_price = data["win"]["price"]
win_score = data["win"]["score"]
win_decision = data["win"]["decision"]
```

---

## Tratamento de Erros

O módulo trata automaticamente:

1. **Células vazias**: Retorna `0.0` ou `None`
2. **Erros do Excel** (`#N/A`, `#VALUE!`): Retorna valor padrão
3. **Strings numéricas**: Converte automaticamente
4. **Excel não aberto**: Lança exceção clara

---

## Vantagens vs Cálculo Manual

| Aspecto | Cálculo Manual | Profit RTD |
|---------|----------------|------------|
| **Performance** | Lento (muitos cálculos) | Rápido (leitura direta) |
| **Precisão** | Depende da implementação | Garantida pelo Profit Pro |
| **Manutenção** | Alta (bugs, ajustes) | Baixa (Profit já testado) |
| **Indicadores** | Limitado | Acesso a todos do Profit |
| **Latência** | ~500ms | ~50ms |

---

## Próximos Passos

1. ✅ Criar `profit-data.xlsx` com RTD configurado
2. ✅ Testar `python profit_bridge.py`
3. ⏳ Integrar com `data_engine.py`
4. ⏳ Substituir cálculos manuais por dados do Profit
