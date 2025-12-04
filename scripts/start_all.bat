@echo off
echo 🚀 Iniciando AI-TRADER-PRO (Full Stack)...

:: 1. Iniciar Docker Compose
echo 🐳 Subindo containers Docker...
docker-compose -f docker-compose.dev.yml up -d --build

:: 2. Iniciar Bridge em nova janela
echo 🌉 Iniciando Bridge (MT5 + Scraping)...
start "AI-TRADER-PRO Bridge" cmd /k "python scripts/bridge.py"

echo ✅ Tudo iniciado!
echo 🌐 Frontend: http://localhost:3000
echo 📊 Bridge rodando na outra janela.
pause
