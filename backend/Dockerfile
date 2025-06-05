FROM python:3.11-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o requirements.txt e instala as dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o conteúdo do backend para dentro do container
COPY . .

# Comando para iniciar o FastAPI com Uvicorn
CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "8000"]
