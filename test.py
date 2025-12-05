import random
import pandas as pd

# --- 1. CONFIGURAÇÃO (Sua Base de Conhecimento) ---
BROKER_GROUPS = {
    "FOREIGN": [16, 114, 45, 306, 23, 40, 127],      # UBS, JP, Credit...
    "INSTITUTIONAL": [85, 113, 72, 27, 39, 92, 111], # BTG, Itau, Bradesco...
    "RETAIL": [308, 386, 1982, 15, 147, 107, 1099],  # Clear, Rico, Modal...
    # XP (3) e Genial (120) são mistos, vamos ignorar ou tratar separado
}

# Mapeamento reverso para exibir nomes (Opcional, só para visualização)
BROKER_NAMES = {
    16: "UBS", 114: "JP MORGAN", 45: "CREDIT", 308: "CLEAR", 
    85: "BTG", 113: "ITAU", 3: "XP", 306: "MERRILL"
}

def get_player_group(broker_id):
    """Retorna o grupo do player baseado no ID da corretora."""
    for group, ids in BROKER_GROUPS.items():
        if broker_id in ids:
            return group
    return "OTHER" # Misto ou Desconhecido

# --- 2. SIMULAÇÃO DE DADOS (O "Mock" do MT5) ---
def generate_fake_trades(n=100):
    print(f"🎲 Gerando {n} negócios simulados...")
    trades = []
    
    # Lista de corretoras ativas no teste
    active_brokers = [16, 114, 308, 85, 113, 3, 306, 15] 
    
    for _ in range(n):
        # Simula um negócio
        buyer = random.choice(active_brokers)
        seller = random.choice(active_brokers)
        
        # Evita auto-negociação (mesma corretora)
        while seller == buyer:
            seller = random.choice(active_brokers)
            
        volume = random.randint(1, 50) # Lotes de 1 a 50
        price = 5500.0 + random.uniform(-10, 10) # Preço base WDO
        
        trades.append({
            "buyer_id": buyer,
            "seller_id": seller,
            "volume": volume,
            "price": price
        })
    
    return trades

# --- 3. MOTOR DE CÁLCULO (A Lógica do seu Backend) ---
def calculate_flow(trades):
    print("⚙️ Processando fluxo de ordens...")
    
    # Inicializa saldos
    scores = {
        "FOREIGN": 0,
        "INSTITUTIONAL": 0,
        "RETAIL": 0,
        "OTHER": 0
    }
    
    detailed_flow = []

    for t in trades:
        buyer_group = get_player_group(t['buyer_id'])
        seller_group = get_player_group(t['seller_id'])
        vol = t['volume']
        
        # Lógica de Saldo:
        # Se Gringo Compra (+Vol)
        # Se Gringo Vende (-Vol)
        
        scores[buyer_group] += vol
        scores[seller_group] -= vol
        
        # Log detalhado (opcional)
        # print(f"{BROKER_NAMES.get(t['buyer_id'], t['buyer_id'])} ({buyer_group}) comprou {vol} de {BROKER_NAMES.get(t['seller_id'], t['seller_id'])} ({seller_group})")

    return scores

# --- 4. EXECUÇÃO ---
if __name__ == "__main__":
    # 1. Gera dados
    fake_data = generate_fake_trades(200)
    
    # 2. Calcula
    results = calculate_flow(fake_data)
    
    # 3. Exibe Relatório (Como apareceria no Dashboard)
    print("\n" + "="*40)
    print("📊 PLACAR DO FLUXO (Saldo Líquido)")
    print("="*40)
    
    for group, score in results.items():
        bar = "🟦" if score > 0 else "🟥"
        print(f"{bar} {group.ljust(15)}: {score:+d} contratos")
        
    print("-" * 40)
    
    # 4. Análise Automática (O "Cérebro" do Dashboard)
    gringo_score = results["FOREIGN"]
    retail_score = results["RETAIL"]
    
    print("\n🤖 ANÁLISE DO JARVIS:")
    if gringo_score > 500:
        print("✅ ESTRANGEIROS COMPRANDO FORTE -> Tendência de ALTA.")
    elif gringo_score < -500:
        print("🔻 ESTRANGEIROS VENDENDO FORTE -> Tendência de BAIXA.")
    else:
        print("⚠️ ESTRANGEIROS NEUTROS -> Mercado sem direção clara.")
        
    if (gringo_score > 0 and retail_score < 0) or (gringo_score < 0 and retail_score > 0):
        print("💎 DIVERGÊNCIA CLÁSSICA DETECTADA (Gringo vs Varejo). Sinal Confiável!")
    else:
        print("⚠️ SEM DIVERGÊNCIA CLARA. Cuidado.")