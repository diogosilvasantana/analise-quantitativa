import MetaTrader5 as mt5
import datetime
import pandas as pd

def test_calendar():
    if not mt5.initialize():
        print(f"❌ Falha ao inicializar MT5: {mt5.last_error()}")
        return

    print("✅ MT5 Inicializado")
    print(f"Terminal: {mt5.terminal_info().name}")
    print(f"Corretora: {mt5.account_info().company}")

    # 1. Buscar Eventos (Metadados)
    # Filtra por moeda (USD, BRL)
    print("\n🔍 Buscando eventos (USD, BRL)...")
    events = mt5.calendar_events(country_code="US")
    events_br = mt5.calendar_events(country_code="BR")
    
    if events is None:
        print("⚠️ calendar_events(US) retornou None")
        events = []
    if events_br is None:
        print("⚠️ calendar_events(BR) retornou None")
        events_br = []
        
    all_events = list(events) + list(events_br)
    print(f"Encontrados {len(all_events)} definições de eventos.")

    # 2. Buscar Valores para Hoje
    now = datetime.datetime.now()
    start = datetime.datetime(now.year, now.month, now.day)
    end = start + datetime.timedelta(days=1)
    
    print(f"\n🔍 Buscando valores de {start} até {end}...")
    
    try:
        values = mt5.calendar_values(start, end)
        if values is None:
             print("❌ calendar_values retornou None. A corretora pode não fornecer dados.")
        else:
            print(f"✅ Encontrados {len(values)} eventos agendados para hoje!")
            
            # Exibir os primeiros 5
            for val in values[:5]:
                # Encontrar nome do evento
                event_meta = next((e for e in all_events if e.id == val.event_id), None)
                name = event_meta.name if event_meta else "Desconhecido"
                currency = event_meta.currency if event_meta else "??"
                importance = event_meta.importance if event_meta else 0
                
                print(f"🕒 {val.time} | {currency} | Imp: {importance} | {name} | Atual: {val.actual_value}")

    except Exception as e:
        print(f"❌ Erro ao buscar valores: {e}")

    mt5.shutdown()

if __name__ == "__main__":
    test_calendar()
