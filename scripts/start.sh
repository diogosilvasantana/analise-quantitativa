#!/bin/bash
set -e

echo "🚀 Iniciando AI-TRADER-PRO..."

# Criar .env se não existir
if [ ! -f backend/.env ]; then
  cp backend/.env.example backend/.env
  echo "✅ Arquivo .env criado em backend/.env"
fi

# Iniciar Docker Compose
docker-compose -f docker-compose.dev.yml up -d --build

echo "✅ Serviços iniciados!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔌 Backend API: http://localhost:8000/api/dashboard_data"
echo "📊 Backend WebSocket: ws://localhost:8000/ws/dashboard"
echo "🚀 Health Check: http://localhost:8000/health"
echo "⚠️ Lembre-se de iniciar o MetaTrader 5 com o Expert Advisor!"
