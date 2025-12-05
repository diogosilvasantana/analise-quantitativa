@echo off
echo 🚀 Iniciando AI-TRADER-PRO (Full Stack)...

:: 1. Iniciar Docker Compose
echo 🐳 Subindo containers Docker...
docker-compose -f docker-compose.dev.yml up -d --build

:: 2. Iniciar Bridge em nova janela
echo 🌉 Iniciando Bridge (MT5 + Scraping)...
start "AI-TRADER-PRO Bridge" cmd /k "python scripts/bridge.py"

:: 3. Iniciar AI Analyst (Agora via Docker)
:: echo 🤖 Iniciando Jarvis Trader (AI Analyst)...
:: start "AI-TRADER-PRO Analyst" cmd /k "python ai-analyst/main.py"

echo ✅ Tudo iniciado!
echo 🌐 Frontend V2: http://localhost:3001
echo 📊 Bridge rodando na outra janela.
pause
