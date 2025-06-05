# frontend/Dockerfile
# Usar uma imagem base oficial do Node.js
FROM node:20-alpine

# Definir o diretório de trabalho
WORKDIR /app

# Copiar os arquivos package.json e package-lock.json para instalar dependências
COPY package*.json ./

# Instalar as dependências do Node.js
RUN npm install

# Copiar o restante do código da aplicação
COPY . .

# Expor a porta que o aplicativo React usa
EXPOSE 3000

# Comando para iniciar o servidor de desenvolvimento React
# Este comando pode ser sobrescrito no docker-compose.yml para 'npm run build' em produção
CMD ["npm", "start"]