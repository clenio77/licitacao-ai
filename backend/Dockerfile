# backend/Dockerfile
# Usar uma imagem base oficial do Python para um ambiente leve e consistente
FROM python:3.10-slim-bookworm

# Definir o diretório de trabalho dentro do container
WORKDIR /app

# Copiar os arquivos de dependência primeiro para aproveitar o cache do Docker
# Copia o requirements.txt do diret diretório pai para o diretório de trabalho do build
COPY requirements.txt .

# Instalar as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Instalar o Playwright e os browsers necessários
RUN pip install playwright
RUN playwright install --with-deps chromium # Instala Chromium com suas dependências de sistema

# Copiar o restante do código do backend para o diretório de trabalho
# O 'context: ./backend' no docker-compose.yml faz com que esta pasta seja o ROOT do build.
# Então, aqui copiamos todo o conteúdo de 'backend' para /app.
COPY . /app

# Definir as portas que o container vai expor (FastAPI)
EXPOSE 8000

# Comando padrão para iniciar a API FastAPI
# Este comando pode ser sobrescrito pelo `command` no docker-compose.yml
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "api.app:app", "--bind", "0.0.0.0:8000"]