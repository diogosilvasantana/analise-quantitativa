"""
Teste Simples - Conexão com Profit Pro Excel (Atualizado)
==========================================================
Script de teste para verificar se consegue conectar e ler dados do Excel.

Uso: python test_profit_connection.py
"""

import win32com.client
import sys

print("=" * 60)
print("TESTE DE CONEXÃO - PROFIT PRO EXCEL")
print("=" * 60)
print()

try:
    # 1. Tentar conectar ao Excel (método melhorado)
    print("1️⃣ Tentando conectar ao Excel...")
    
    try:
        excel = win32com.client.GetObject(None, "Excel.Application")
        print("   ✅ Conectado via GetObject")
    except:
        excel = win32com.client.Dispatch("Excel.Application")
        print("   ✅ Conectado via Dispatch")
    
    print(f"   Versão: {excel.Version}")
    print()
    
    # 2. Verificar workbooks
    print("2️⃣ Verificando arquivos abertos...")
    if excel.Workbooks.Count == 0:
        print("   ❌ NENHUM arquivo Excel aberto!")
        print("   💡 Pressione Ctrl+N no Excel para criar um novo arquivo")
        sys.exit(1)
    
    print(f"   ✅ {excel.Workbooks.Count} arquivo(s) aberto(s)")
    print()
    
    # 3. Listar workbooks
    print("3️⃣ Arquivos abertos:")
    for i in range(1, excel.Workbooks.Count + 1):
        wb = excel.Workbooks(i)
        print(f"   [{i}] {wb.Name}")
    print()
    
    # 4. Usar primeiro workbook
    wb = excel.Workbooks(1)
    print(f"4️⃣ Usando: {wb.Name}")
    print()
    
    # 5. Listar planilhas
    print("5️⃣ Planilhas:")
    try:
        for i in range(1, wb.Worksheets.Count + 1):
            sheet = wb.Worksheets(i)
            print(f"   [{i}] {sheet.Name}")
    except Exception as e:
        print(f"   Erro listando planilhas: {e}")
    print()
    
    # 6. Ler primeira planilha
    sheet = wb.Worksheets(1)
    print(f"6️⃣ Lendo planilha: {sheet.Name}")
    print()
    
    # Testar leitura de células
    print("📊 Testando leitura:")
    test_cells = ["A1", "B2", "G2", "H2", "L2", "Q2", "R2"]
    
    for cell in test_cells:
        try:
            value = sheet.Range(cell).Value
            if value is None:
                print(f"   {cell}: (vazio)")
            else:
                print(f"   {cell}: {value}")
        except Exception as e:
            print(f"   {cell}: ❌ Erro - {e}")
    
    print()
    print("=" * 60)
    print("✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("=" * 60)
    print()
    print("💡 Próximos passos:")
    print("   1. Se as células estão vazias, popule com dados do Profit Pro")
    print("   2. Execute: python scripts/bridge_core/profit_bridge.py")
    print("   3. Ou reinicie o Bridge para usar dados do Excel")
    
except Exception as e:
    print()
    print("=" * 60)
    print("❌ ERRO NO TESTE")
    print("=" * 60)
    print(f"Erro: {e}")
    print()
    print("💡 Soluções:")
    print("   1. Certifique-se que o Excel está aberto")
    print("   2. Crie um novo arquivo (Ctrl+N) no Excel")
    print("   3. Execute este script como Administrador se necessário")
    print()
    sys.exit(1)
