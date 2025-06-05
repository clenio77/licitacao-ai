# Sistema de Busca e Análise de Licitações dos Correios

Este projeto consiste em um backend (FastAPI + Scraping + OpenAI) e um frontend (React) para busca, análise automática e visualização de licitações dos Correios.

## Estrutura do Projeto

- `correios_licitacoes_mvp/backend/` — Backend FastAPI (API, scraping, banco SQLite, integração OpenAI)
- `correios_licitacoes_mvp/frontend/` — Frontend React (tabela, busca, modal de detalhes, geração/baixa de análises)

---

## Deploy no Render.com

### 1. Suba o código para um repositório no GitHub

### 2. Backend (FastAPI)

- **Crie um novo Web Service no Render**
- **Root Directory:** `correios_licitacoes_mvp/backend`
- **Build Command:** (deixe em branco se usar Dockerfile)
- **Start Command:** (deixe em branco se usar Dockerfile ou Procfile)
- **Dockerfile:** já incluso
- **Procfile:** já incluso
- **Variáveis de ambiente:**
  - `OPENAI_API_KEY` (obrigatório)
  - Outras, se necessário
- **Banco de dados:** O backend usa SQLite por padrão (armazenado no container). Para produção, considere migrar para PostgreSQL e ajustar a string de conexão.

#### Exemplo de `.env` para backend:
```
OPENAI_API_KEY=sua_chave_openai
```

### 3. Frontend (React)

- **Crie um novo Web Service ou Static Site no Render**
- **Root Directory:** `correios_licitacoes_mvp/frontend`
- **Build Command:**
  - Para Static Site: `npm install && npm run build`
  - Para Web Service: `npm install`
- **Start Command:**
  - Para Static Site: deixe em branco
  - Para Web Service: `npm start` (Procfile já incluso)
- **Diretório de saída (Static Site):** `build`
- **Variáveis de ambiente:**
  - `REACT_APP_API_URL=https://seu-backend-no-render.onrender.com/api`

#### Exemplo de `.env` para frontend:
```
REACT_APP_API_URL=https://seu-backend-no-render.onrender.com/api
```

### 4. Ajuste de CORS no Backend

No arquivo `api/app.py`, ajuste a lista `allow_origins` para incluir o domínio do frontend no Render, por exemplo:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://seu-frontend-no-render.onrender.com",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Observações
- O backend expõe a API na porta 8000.
- O frontend React roda na porta 3000 (desenvolvimento) ou como site estático em produção.
- O scraping dos Correios pode ser bloqueado por captcha em detalhes, mas a lista principal é coletada normalmente.
- As análises automáticas usam a API da OpenAI (ChatGPT), configure sua chave corretamente.

---

## Dúvidas?
Abra uma issue ou entre em contato! 