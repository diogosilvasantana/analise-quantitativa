"""
Criar Arquivo de Teste no Excel
================================
Este script cria um arquivo de teste diretamente via Python.
"""
import win32com.client
import os

print("=" * 60)
print("CRIANDO ARQUIVO DE TESTE NO EXCEL")
print("=" * 60)
print()

try:
    # Conectar ao Excel
    print("1️⃣ Conectando ao Excel...")
    excel = win32com.client.Dispatch("Excel.Application")
    excel.Visible = True  # Tornar visível
    print("   ✅ Conectado")
    print()
    
    # Criar novo workbook
    print("2️⃣ Criando novo arquivo...")
    wb = excel.Workbooks.Add()
    print("   ✅ Arquivo criado")
    print()
    
    # Pegar primeira planilha
    sheet = wb.Worksheets(1)
    sheet.Name = "Dados"
    
    # Adicionar alguns dados de teste
    print("3️⃣ Adicionando dados de teste...")
    sheet.Range("A1").Value = "Timestamp"
    sheet.Range("B2").Value = 129500  # Preço WIN
    sheet.Range("G2").Value = 2.3     # Bear Power
    sheet.Range("H2").Value = 8.5     # Bull Power
    sheet.Range("Q2").Value = 11.2    # Score
    sheet.Range("R2").Value = "COMPRA AUTORIZADA"  # Decisão
    print("   ✅ Dados adicionados")
    print()
    
    # Salvar
    file_path = os.path.join(os.getcwd(), "profit-data.xlsx")
    print(f"4️⃣ Salvando em: {file_path}")
    wb.SaveAs(file_path)
    print("   ✅ Arquivo salvo")
    print()
    
    print("=" * 60)
    print("✅ ARQUIVO CRIADO COM SUCESSO!")
    print("=" * 60)
    print()
    print(f"📁 Arquivo: {file_path}")
    print()
    print("💡 Próximos passos:")
    print("   1. O arquivo está aberto no Excel")
    print("   2. Execute: python test_profit_connection.py")
    print("   3. Ou execute: python scripts/bridge_core/profit_bridge.py")
    
except Exception as e:
    print()
    print("❌ ERRO:", e)
    import traceback
    traceback.print_exc()
