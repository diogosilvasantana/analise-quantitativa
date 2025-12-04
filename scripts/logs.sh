#!/bin/bash

echo "📊 Logs do Backend:"
docker-compose -f docker-compose.dev.yml logs -f backend
