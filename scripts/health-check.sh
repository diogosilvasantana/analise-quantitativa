#!/bin/bash
echo "Running health checks for AI-TRADER-PRO services..."

# Check Backend Health Endpoint
echo -n "Checking Backend Health (http://localhost:8000/health)... "
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health)
if [ "$HTTP_STATUS" -eq 200 ]; then
    echo "SUCCESS (Status: $HTTP_STATUS)"
else
    echo "FAILED (Status: $HTTP_STATUS)"
fi

# Check Backend Data Endpoint
echo -n "Checking Backend Data (http://localhost:8000/api/dashboard_data)... "
DATA_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/dashboard_data)
if [ "$DATA_STATUS" -eq 200 ]; then
    echo "SUCCESS (Status: $DATA_STATUS)"
else
    echo "FAILED (Status: $DATA_STATUS)"
fi

# Check Frontend accessibility
echo -n "Checking Frontend (http://localhost:3000)... "
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
if [ "$FRONTEND_STATUS" -eq 200 ]; then
    echo "SUCCESS (Status: $FRONTEND_STATUS)"
else
    echo "FAILED (Status: $FRONTEND_STATUS)"
fi

# Check Redis connection (from backend container perspective)
echo -n "Checking Redis connection (from backend)... "
REDIS_CHECK=$(docker-compose -f docker-compose.dev.yml exec -T backend redis-cli -h redis ping 2>/dev/null)
if [ "$REDIS_CHECK" == "PONG" ]; then
    echo "SUCCESS"
else
    echo "FAILED"
fi

echo "Health checks complete."
