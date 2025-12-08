"""
Debug Excel - Mostra todas as instâncias
"""
import win32com.client
import pythoncom

print("=" * 60)
print("DEBUG - INSTÂNCIAS DO EXCEL")
print("=" * 60)
print()

# Método 1: Dispatch
print("1️⃣ Via Dispatch:")
try:
    excel = win32com.client.Dispatch("Excel.Application")
    print(f"   Workbooks: {excel.Workbooks.Count}")
    if excel.Workbooks.Count > 0:
        for i in range(1, excel.Workbooks.Count + 1):
            print(f"   - {excel.Workbooks(i).Name}")
except Exception as e:
    print(f"   Erro: {e}")

print()

# Método 2: GetActiveObject
print("2️⃣ Via GetActiveObject:")
try:
    excel = win32com.client.GetActiveObject("Excel.Application")
    print(f"   Workbooks: {excel.Workbooks.Count}")
    if excel.Workbooks.Count > 0:
        for i in range(1, excel.Workbooks.Count + 1):
            print(f"   - {excel.Workbooks(i).Name}")
except Exception as e:
    print(f"   Erro: {e}")

print()
print("💡 SOLUÇÃO:")
print("   1. Feche TODAS as janelas do Excel")
print("   2. Abra APENAS UMA janela do Excel")
print("   3. Crie um arquivo novo (Ctrl+N)")
print("   4. Salve (Ctrl+S) como 'test.xlsx'")
print("   5. Execute: python test_profit_connection.py")
