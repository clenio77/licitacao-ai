# backend/Dockerfile
# Usar uma imagem base oficial do Python para um ambiente leve e consistente
FROM python:3.11-slim

# Definir o diretório de trabalho dentro do container
WORKDIR /app

# Copiar os arquivos de dependência primeiro para aproveitar o cache do Docker
# Copia o requirements.txt do diret diretório pai para o diretório de trabalho do build
COPY requirements.txt .

# Instalar as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do código do backend para o diretório de trabalho
# O 'context: ./backend' no docker-compose.yml faz com que esta pasta seja o ROOT do build.
# Então, aqui copiamos todo o conteúdo de 'backend' para /app.
COPY . .

# Definir as portas que o container vai expor (FastAPI)
EXPOSE 8000

# Comando padrão para iniciar a API FastAPI
# Este comando pode ser sobrescrito pelo `command` no docker-compose.yml
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]