# Use a imagem oficial do Node.js como base
FROM node:18-alpine

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia package.json e package-lock.json (se existir)
COPY ./frontend/package*.json ./

# Instala as dependências
RUN npm install

# Copia o restante do código da aplicação
COPY ./frontend .

# Constrói a aplicação React para produção
RUN npm run build

# Expõe a porta que a aplicação React vai usar
EXPOSE 3000

# Comando para iniciar a aplicação (será sobrescrito pelo docker-compose para desenvolvimento)
CMD ["npm", "run", "dev", "--", "--host"]
