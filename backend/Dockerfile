# Use a imagem oficial do Python como base
FROM python:3.11-slim-buster

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo requirements.txt para o diretório de trabalho
COPY ./backend/requirements.txt /app/requirements.txt

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da aplicação
COPY ./backend/src /app/src

# Expõe a porta que a aplicação FastAPI vai usar
EXPOSE 8000

# Comando para iniciar a aplicação (será sobrescrito pelo docker-compose para desenvolvimento)
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
