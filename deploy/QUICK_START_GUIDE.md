# 🚀 Guia de Deploy Rápido - 10 Minutos

## 🎯 Deploy Gratuito Completo

**Sistema online em 10 minutos com $0/mês!**

### ⚡ Opção 1: Deploy Automático (Recomendado)

```bash
# 1. Executar script automático
./deploy/scripts/deploy-free-tier.sh

# 2. Escolher opção 1 (Deploy completo)
# 3. Seguir instruções na tela
```

### 🛠️ Opção 2: Deploy Manual

#### 📦 **Passo 1: Frontend no Vercel (2 minutos)**

```bash
# 1. Instalar Vercel CLI
npm install -g vercel

# 2. Deploy do frontend
cd frontend
npm install
npm run build
vercel --prod

# 3. Configurar domínio (opcional)
vercel domains add licitacao-correios.com
```

**✅ Frontend online em:** `https://seu-projeto.vercel.app`

#### 🐍 **Passo 2: Backend no Railway (3 minutos)**

```bash
# 1. Acessar https://railway.app
# 2. Conectar repositório GitHub
# 3. Selecionar pasta 'backend'
# 4. Configurar variáveis de ambiente:

DATABASE_URL=postgresql://...  # Do Supabase
REDIS_URL=redis://...          # Do Upstash
SECRET_KEY=sua-chave-secreta
OPENAI_API_KEY=sua-chave-openai
```

**✅ Backend online em:** `https://seu-projeto.railway.app`

#### 🐘 **Passo 3: Banco no Supabase (3 minutos)**

```bash
# 1. Acessar https://supabase.com
# 2. Criar novo projeto
# 3. Executar SQL no editor:

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE editais (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    objeto TEXT NOT NULL,
    categoria VARCHAR(50),
    valor_estimado DECIMAL(15,2),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE feedback_setor (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    edital_id UUID REFERENCES editais(id),
    setor_nome VARCHAR(255) NOT NULL,
    facilidade_uso INTEGER CHECK (facilidade_uso >= 1 AND facilidade_uso <= 5),
    created_at TIMESTAMP DEFAULT NOW()
);
```

**✅ Banco online em:** `postgresql://...`

#### 🔴 **Passo 4: Cache no Upstash (2 minutos)**

```bash
# 1. Acessar https://upstash.com
# 2. Criar conta gratuita
# 3. Criar banco Redis
# 4. Copiar REDIS_URL
```

**✅ Cache online em:** `redis://...`

---

## 🌐 Plataformas Alternativas

### 🔥 **Firebase (Google)**

```bash
# 1. Instalar Firebase CLI
npm install -g firebase-tools

# 2. Login e inicializar
firebase login
firebase init hosting

# 3. Deploy
firebase deploy
```

**Recursos Gratuitos:**
- Hosting: 10 GB/mês
- Functions: 2M invocações/mês
- Firestore: 1 GB storage

### ☁️ **Netlify**

```bash
# 1. Conectar GitHub no Netlify
# 2. Configurar build:
#    Build command: npm run build
#    Publish directory: build
# 3. Deploy automático no push
```

**Recursos Gratuitos:**
- 100 GB bandwidth/mês
- 300 build minutes/mês
- Forms e Functions incluídos

### 🌊 **Render**

```bash
# 1. Conectar GitHub no Render
# 2. Criar Web Service
# 3. Configurar:
#    Build Command: pip install -r requirements.txt
#    Start Command: uvicorn api.app:app --host 0.0.0.0 --port $PORT
```

**Recursos Gratuitos:**
- 512 MB RAM
- Sleep após 15min inatividade
- PostgreSQL gratuito (90 dias)

---

## 📊 Comparativo Rápido

| Plataforma | Setup | Custo | Performance | Recomendação |
|------------|-------|-------|-------------|--------------|
| **Vercel + Railway** | 5 min | $0 | ⭐⭐⭐⭐ | 🥇 **Melhor** |
| **Netlify + Render** | 7 min | $0 | ⭐⭐⭐ | 🥈 Alternativa |
| **Firebase** | 10 min | $0 | ⭐⭐⭐⭐ | 🥉 Google Lock-in |
| **DigitalOcean** | 15 min | $6/mês | ⭐⭐⭐⭐⭐ | 💰 Pago |

---

## 🔧 Configurações Essenciais

### 🌍 **Variáveis de Ambiente**

```bash
# Frontend (Vercel)
REACT_APP_API_URL=https://seu-backend.railway.app/api
REACT_APP_ENVIRONMENT=production

# Backend (Railway)
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://user:pass@host:6379
SECRET_KEY=sua-chave-super-secreta-aqui
JWT_SECRET_KEY=sua-chave-jwt-aqui
OPENAI_API_KEY=sk-...
ENVIRONMENT=production
DEBUG=false
```

### 🔒 **Configurações de Segurança**

```bash
# CORS Origins (Backend)
ALLOWED_ORIGINS=https://seu-frontend.vercel.app,https://www.correios.com.br

# Headers de Segurança (Vercel)
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
```

### 📊 **Monitoramento Gratuito**

```bash
# Sentry (Error Tracking)
SENTRY_DSN=https://...@sentry.io/...

# Grafana Cloud (Métricas)
GRAFANA_CLOUD_API_KEY=glc_...

# Uptime Robot (Monitoring)
# Configurar no site: https://uptimerobot.com
```

---

## 🚨 Troubleshooting

### ❌ **Problemas Comuns**

#### **Build Falha no Vercel**
```bash
# Solução: Verificar Node.js version
echo "node: 18.x" > .nvmrc

# Ou configurar no vercel.json
{
  "functions": {
    "app/**/*.js": {
      "runtime": "nodejs18.x"
    }
  }
}
```

#### **Backend não conecta no Railway**
```bash
# Verificar variáveis de ambiente
railway variables

# Verificar logs
railway logs

# Testar localmente
railway run python -m uvicorn api.app:app --port 8000
```

#### **Banco não conecta no Supabase**
```bash
# Verificar connection string
psql "postgresql://user:pass@host:5432/db"

# Verificar RLS (Row Level Security)
# Desabilitar temporariamente para teste
ALTER TABLE editais DISABLE ROW LEVEL SECURITY;
```

#### **CORS Error**
```bash
# Adicionar origem no backend
ALLOWED_ORIGINS=https://seu-frontend.vercel.app

# Ou configurar no código
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://seu-frontend.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📈 Próximos Passos

### 🔄 **Após Deploy**

1. **Configurar Domínio Personalizado**
   ```bash
   # Vercel
   vercel domains add licitacao-correios.com
   
   # Railway
   # Configurar no dashboard
   ```

2. **Configurar SSL/HTTPS**
   ```bash
   # Automático no Vercel e Railway
   # Verificar certificado válido
   ```

3. **Configurar Backup**
   ```bash
   # Supabase: Backup automático incluído
   # Configurar backup adicional se necessário
   ```

4. **Monitoramento**
   ```bash
   # Configurar alertas no Grafana Cloud
   # Configurar Uptime Robot
   # Configurar Sentry para errors
   ```

### 🚀 **Otimizações**

1. **Performance**
   - Ativar CDN no Vercel
   - Configurar cache headers
   - Otimizar imagens

2. **SEO**
   - Configurar meta tags
   - Sitemap.xml
   - robots.txt

3. **Analytics**
   - Google Analytics
   - Hotjar para UX
   - Métricas customizadas

---

## 📞 **Suporte**

### 🆘 **Precisa de Ajuda?**

1. **Documentação Oficial**
   - [Vercel Docs](https://vercel.com/docs)
   - [Railway Docs](https://docs.railway.app)
   - [Supabase Docs](https://supabase.com/docs)

2. **Comunidade**
   - [Vercel Discord](https://vercel.com/discord)
   - [Railway Discord](https://discord.gg/railway)
   - [Supabase Discord](https://discord.supabase.com)

3. **Issues GitHub**
   - Criar issue no repositório
   - Incluir logs e configurações
   - Marcar como bug ou question

---

## 🎉 **Resultado Final**

**✅ Sistema completo online em 10 minutos:**

- 🌐 **Frontend**: `https://licitacao-correios.vercel.app`
- 🔧 **Backend**: `https://licitacao-backend.railway.app`
- 🗄️ **Banco**: Supabase PostgreSQL
- ⚡ **Cache**: Upstash Redis
- 📊 **Monitoramento**: Grafana Cloud + Sentry

**💰 Custo total: $0/mês**

**🚀 Pronto para receber milhares de usuários!**
