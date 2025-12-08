"""
Teste Avançado - Conexão Excel com Múltiplos Métodos
=====================================================
Tenta diferentes formas de conectar ao Excel.
"""

import sys

print("=" * 60)
print("TESTE AVANÇADO - CONEXÃO EXCEL")
print("=" * 60)
print()

# Método 1: win32com.client (Padrão)
print("🔍 Método 1: win32com.client.GetObject()")
try:
    import win32com.client
    excel = win32com.client.GetObject(None, "Excel.Application")
    print("   ✅ SUCESSO!")
    print(f"   Excel Versão: {excel.Version}")
    print(f"   Workbooks: {excel.Workbooks.Count}")
    if excel.Workbooks.Count > 0:
        wb = excel.Workbooks(1)
        print(f"   Arquivo: {wb.Name}")
        sheet = wb.Worksheets(1)
        print(f"   Planilha: {sheet.Name}")
        
        # Testar leitura
        print()
        print("   📊 Testando leitura:")
        for cell in ["A1", "B2", "G2", "H2"]:
            val = sheet.Range(cell).Value
            print(f"      {cell}: {val}")
    excel = None
except Exception as e:
    print(f"   ❌ FALHOU: {e}")

print()

# Método 2: win32com.client.Dispatch
print("🔍 Método 2: win32com.client.Dispatch()")
try:
    import win32com.client
    excel = win32com.client.Dispatch("Excel.Application")
    print("   ✅ SUCESSO!")
    print(f"   Excel Versão: {excel.Version}")
    print(f"   Workbooks: {excel.Workbooks.Count}")
    excel.Quit()
except Exception as e:
    print(f"   ❌ FALHOU: {e}")

print()

# Método 3: win32com.client.gencache
print("🔍 Método 3: win32com.client.gencache.EnsureDispatch()")
try:
    import win32com.client
    excel = win32com.client.gencache.EnsureDispatch("Excel.Application")
    print("   ✅ SUCESSO!")
    print(f"   Excel Versão: {excel.Version}")
    excel.Quit()
except Exception as e:
    print(f"   ❌ FALHOU: {e}")

print()
print("=" * 60)
print("DIAGNÓSTICO")
print("=" * 60)
print()

# Verificar privilégios
try:
    import ctypes
    is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    print(f"Python rodando como Admin: {'✅ SIM' if is_admin else '❌ NÃO'}")
except:
    print("Python rodando como Admin: ❓ Não foi possível verificar")

print()
print("💡 SOLUÇÕES:")
print()
print("Se TODOS os métodos falharam:")
print("   1. Feche o Excel")
print("   2. Feche este terminal")
print("   3. Abra PowerShell como Administrador:")
print("      - Clique direito no PowerShell")
print("      - 'Executar como Administrador'")
print("   4. Navegue até a pasta:")
print("      cd e:\\projetos\\ai-trader-pro")
print("   5. Abra o Excel (SEM privilégios de admin)")
print("   6. Execute novamente:")
print("      python test_profit_connection.py")
print()
print("OU (Alternativa):")
print("   - Use o sistema sem Profit Pro (já está funcionando!)")
print("   - Dados vêm direto do MT5")
