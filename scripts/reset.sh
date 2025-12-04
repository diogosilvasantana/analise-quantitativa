#!/bin/bash
set -e

echo "🔄 Resetando ambiente (parando, removendo volumes e reconstruindo)..."
docker-compose -f docker-compose.dev.yml down -v --rmi all
docker-compose -f docker-compose.dev.yml up -d --build

echo "✅ Ambiente resetado e serviços reiniciados."
