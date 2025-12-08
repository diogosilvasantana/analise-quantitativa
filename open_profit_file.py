"""
Abrir profit-data.xlsx no Excel
================================
"""
import win32com.client
import os

file_path = r"e:\projetos\ai-trader-pro\profit-data.xlsx"

print("=" * 60)
print("ABRINDO PROFIT-DATA.XLSX")
print("=" * 60)
print()

try:
    # Verificar se arquivo existe
    if not os.path.exists(file_path):
        print(f"❌ Arquivo não encontrado: {file_path}")
        exit(1)
    
    print(f"📁 Arquivo: {file_path}")
    print()
    
    # Conectar ao Excel
    print("1️⃣ Conectando ao Excel...")
    excel = win32com.client.Dispatch("Excel.Application")
    excel.Visible = True
    print("   ✅ Excel conectado")
    print()
    
    # Abrir arquivo
    print("2️⃣ Abrindo arquivo...")
    wb = excel.Workbooks.Open(file_path)
    print(f"   ✅ Arquivo aberto: {wb.Name}")
    print()
    
    # Listar planilhas
    print("3️⃣ Planilhas disponíveis:")
    for i in range(1, wb.Worksheets.Count + 1):
        try:
            sheet = wb.Worksheets(i)
            print(f"   [{i}] {sheet.Name}")
        except:
            print(f"   [{i}] (erro ao ler nome)")
    print()
    
    print("=" * 60)
    print("✅ ARQUIVO ABERTO COM SUCESSO!")
    print("=" * 60)
    print()
    print("💡 Próximos passos:")
    print("   1. Configure RTD no Profit Pro para este arquivo")
    print("   2. Execute: python test_profit_connection.py")
    print("   3. Ou execute: python scripts/bridge_core/profit_bridge.py")
    print()
    print("⚠️ NÃO FECHE o Excel! Deixe o arquivo aberto.")
    
except Exception as e:
    print()
    print("❌ ERRO:", e)
    import traceback
    traceback.print_exc()
