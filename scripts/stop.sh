#!/bin/bash
set -e

echo "⛔ Parando serviços..."
docker-compose -f docker-compose.dev.yml down

echo "✅ Serviços parados"
