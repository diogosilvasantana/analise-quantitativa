@echo off
echo Parando containers...
docker-compose -f docker-compose.dev.yml down
echo Tudo parado!
pause
