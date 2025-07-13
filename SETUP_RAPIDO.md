# 🚀 Setup Rápido - Sistema de Licitações dos Correios

## 📋 Pré-requisitos

- Python 3.8+
- Node.js 16+ e npm
- Chave da API OpenAI

## ⚡ Instalação Express (5 minutos)

### 1. Clone e Configure o Projeto

```bash
# Navegar para o diretório do projeto
cd correios_licitacoes_mvp

# Criar arquivo de configuração do backend
cp backend/.env.example backend/.env

# Criar arquivo de configuração do frontend
cp frontend/.env.example frontend/.env
```

### 2. Configurar Backend

```bash
# Instalar dependências (use uma das opções abaixo)

# Opção 1: Ambiente isolado (recomendado)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Opção 2: Instalação direta (se não funcionar o venv)
pip install --break-system-packages fastapi uvicorn sqlalchemy openai python-dotenv

# Configurar variáveis de ambiente
echo "OPENAI_API_KEY=sua_chave_aqui" > backend/.env
```

### 3. Configurar Frontend

```bash
cd frontend

# Instalar dependências
npm install

# Configurar URL da API
echo "REACT_APP_API_URL=http://localhost:8000/api" > .env
```

### 4. Executar o Sistema

**Terminal 1 - Backend:**
```bash
cd backend
python3 -m api.app
# ou
uvicorn api.app:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

### 5. Acessar o Sistema

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **Documentação da API:** http://localhost:8000/docs

## 🔧 Configurações Essenciais

### Backend (.env)
```env
OPENAI_API_KEY=sua_chave_openai_aqui
DATABASE_URL=sqlite:///./data/licitacoes.db
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True
```

### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_TITLE=Sistema de Licitações dos Correios
REACT_APP_DEBUG=true
```

## 🎯 Funcionalidades Disponíveis

### ✅ Imediatamente Funcionais
- **Dashboard de Licitações:** Visualização e filtros
- **Busca Manual:** Coleta de licitações dos Correios
- **Análise Automática:** Geração de análises com IA
- **Interface de Feedback:** Sistema de avaliação
- **Base de Conhecimento:** Consulta de padrões

### ⚠️ Requer Configuração Adicional
- **Web Scraping:** Instalar Playwright browsers
- **Notificações:** Configurar webhooks
- **Autenticação:** Implementar sistema de login

## 🔍 Testando o Sistema

### Teste da API
```bash
# Verificar se a API está rodando
curl http://localhost:8000/api/licitacoes/

# Testar geração de análise
curl -X POST http://localhost:8000/api/gerar_analise?id=exemplo
```

### Teste do Frontend
1. Acesse http://localhost:3000
2. Navegue entre as páginas
3. Teste a geração de edital
4. Verifique a base de conhecimento

## 🚨 Problemas Comuns

### Erro de Dependências Python
```bash
# Solução: Instalar com --break-system-packages
pip install --break-system-packages <pacote>
```

### Erro de Porta em Uso
```bash
# Matar processo na porta 8000
sudo lsof -t -i tcp:8000 | xargs kill -9

# Matar processo na porta 3000
sudo lsof -t -i tcp:3000 | xargs kill -9
```

### Erro de CORS
- Verificar se CORS está configurado no backend
- Confirmar URL da API no frontend

### Erro de OpenAI
- Verificar se OPENAI_API_KEY está configurada
- Confirmar se a chave é válida

## 📊 Monitoramento

### Logs do Backend
```bash
# Ver logs em tempo real
tail -f backend/logs/app.log

# Verificar erros
grep ERROR backend/logs/app.log
```

### Logs do Frontend
- Abrir DevTools do navegador (F12)
- Verificar console para erros JavaScript
- Verificar Network tab para erros de API

## 🔄 Restart Rápido

```bash
# Restart do backend
cd backend && python3 -m api.app

# Restart do frontend
cd frontend && npm start
```

## 🎨 Personalização Rápida

### Tema do Frontend
Edite `frontend/src/App.css`:
```css
:root {
  --primary-color: #0066cc;
  --secondary-color: #0052a3;
}
```

### Configurações da API
Edite `backend/api/app.py`:
```python
# Mudar porta
uvicorn.run("app:app", host="0.0.0.0", port=8001)

# Adicionar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"]
)
```

## 📞 Suporte

### Documentação
- **API:** http://localhost:8000/docs
- **Código:** Ver comentários nos arquivos
- **Status:** Consulte STATUS_IMPLEMENTACAO.md

### Logs Úteis
- **Backend:** `backend/logs/app.log`
- **Frontend:** Console do navegador
- **Banco:** `data/licitacoes.db`

---

**🎉 Pronto! O sistema deve estar rodando em http://localhost:3000**

*Tempo total de setup: ~5 minutos*