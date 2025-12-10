import win32com.client
import win32com.server.util
import pythoncom
import time
import threading

# UUID do IRTDUpdateEvent (interface padrão do Excel RTD)
# Geralmente não precisamos registrar se passarmos o objeto Python envolvido corretamente

class RTDUpdateEvent:
    """
    Callback class that simulates Excel's IRTDUpdateEvent interface.
    The RTD Server calls UpdateNotify() on this object to signal new data.
    """
    _public_methods_ = ['UpdateNotify', 'Heartbeat', 'Disconnect']
    
    def __init__(self):
        self.interval = 1000 # Default heartbeat interval
    
    def UpdateNotify(self):
        # O servidor avisa: "Tenho dados novos!"
        # Em resposta, o cliente (nós) deve chamar RefreshData() no servidor
        print("🔔 Callback recebido: UpdateNotify!")
        return 0
        
    def Heartbeat(self):
        print("💓 Callback recebido: Heartbeat")
        return 1 # 1 = Keep alive
    
    def Disconnect(self):
        print("🔌 Callback recebido: Disconnect")

if __name__ == "__main__":
    PROFIT_ID = "RTDTrading.RTDServer"
    
    try:
        # 1. Instanciar o servidor RTD do Profit
        print(f"🔌 Tentando conectar ao {PROFIT_ID}...")
        rtd_server = win32com.client.Dispatch(PROFIT_ID)
        print("✅ Objeto Server criado.")
        
        # 2. Criar nosso objeto de callback e "envelopar" como objeto COM
        print("🛠️ Criando callback COM...")
        callback_obj = RTDUpdateEvent()
        callback_com = win32com.server.util.wrap(callback_obj)
        
        # 3. Iniciar o Server (passando nosso callback)
        print("🚀 Chamando ServerStart...")
        status = rtd_server.ServerStart(callback_com)
        print(f"✅ ServerStart retornou: {status}")
        
        # 4. Assinar Tópicos (Ex: DOL Futuro)
        # Sintaxe: ConnectData(TopicID, Strings, GetNewValues)
        # Strings é uma tupla. Profit usa: [Ativo, Atributo]
        
        # Exemplo da Wiki: DOLFUT_F_0, ABE (Abertura) ou ULT (Ultimo)
        topic_id = 1
        asset = "WDO$N" # Tente WDO$ ou WDO$N dependendo do Profit
        field = "ULT"   # Ultimo Preço
        
        # Strings must be passed as tuple
        strings = (asset, field)
        get_new_values = True
        
        print(f"📡 Assinando tópico: {strings}")
        # Note: Some RTD servers expect specific formatting for strings
        initial_val = rtd_server.ConnectData(topic_id, strings, get_new_values)
        print(f"📥 Valor inicial recebido: {initial_val}")
        
        # Loop para manter vivo e processar mensagens COM
        print("🔄 Entrando no loop de escuta (Ctrl+C para sair)...")
        start_time = time.time()
        while True:
            # Importante: Precisamos bombear mensagens do Windows para o callback funcionar
            pythoncom.PumpWaitingMessages()
            
            # Periodicamente pedimos RefreshData (simulando o Excel perguntando)
            # Na prática real, faríamos apenas quando UpdateNotify fosse chamado
            count = 1
            try:
                # RefreshData retorna uma tupla de tuplas ((TopicID, Value), ...)
                # Ou arrays separados. A assinatura varia.
                # Documentação Excel: RefreshData(TopicCount) -> SafeArray(TopicIDs), SafeArray(Values)
                
                # Vamos tentar chamar apenas se passar um tempo
                if time.time() - start_time > 2:
                    data = rtd_server.RefreshData(count) 
                    # RefreshData retorna (TopicCount, ((ID, Val), ...)) dependendo da implementação COM do Python
                    if data:
                        print(f"📊 RefreshData: {data}")
                    start_time = time.time()
                    
            except Exception as eRefresh:
                # print(f"Refresh error (pode ser normal se vazio): {eRefresh}")
                pass
                
            time.sleep(0.1)
            
    except Exception as e:
        print(f"❌ Erro Fatal: {e}")
        import traceback
        traceback.print_exc()

    finally:
        if 'rtd_server' in locals():
            try:
                rtd_server.ServerTerminate()
                print("🛑 ServerTerminate chamado.")
            except:
                pass
