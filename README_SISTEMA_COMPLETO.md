# 🏛️ Sistema Completo de Licitações dos Correios com IA

## 📋 Visão Geral

Sistema completo e avançado para gestão de licitações dos Correios, integrando:

1. **📊 Análise de Licitações Existentes** - Monitoramento e análise de licitações em andamento
2. **📝 Geração Automatizada de Editais** - Criação inteligente de editais usando IA
3. **🧠 Base de Conhecimento Inteligente** - Web scraping de licitações bem-sucedidas para aprendizado contínuo

## 🚀 Funcionalidades Principais

### 1. Análise de Licitações (Funcionalidade Original)
- Busca automática de licitações dos Correios
- Análise com IA usando OpenAI GPT
- Interface web para visualização
- Armazenamento em banco SQLite

### 2. Geração de Editais com IA (NOVO)
- **Agentes Especializados CrewAI**:
  - 👨‍💼 Coletor de Requisitos
  - ⚖️ Analisador Jurídico  
  - 🔧 Analisador Técnico
  - 💰 Analisador Financeiro
  - ⚠️ Especialista em Riscos
  - 📝 Gerador de Edital
  - 🔧 Revisor e Otimizador
  - 🎯 Coordenador do Processo
  - 🧠 Especialista em Base de Conhecimento

- **Processo Inteligente**:
  1. Coleta e validação de requisitos
  2. Análises especializadas paralelas
  3. Cálculo de risco consolidado
  4. Geração do edital baseada em templates
  5. Otimização com boas práticas
  6. Coordenação final e relatório

### 3. Base de Conhecimento com Web Scraping (NOVO)
- **Coleta Automatizada**:
  - Portal da Transparência
  - ComprasNet (simulado)
  - Dados públicos de licitações

- **Análise Inteligente**:
  - Identificação de padrões de sucesso
  - Extração de fatores críticos
  - Recomendações baseadas em dados
  - Analytics avançados

## 🏗️ Arquitetura do Sistema

```
📁 Sistema de Licitações dos Correios
├── 🖥️ Frontend (React)
│   ├── 📊 Análise de Licitações
│   ├── 📝 Geração de Editais
│   └── 🧠 Base de Conhecimento
├── 🔧 Backend (FastAPI + Python)
│   ├── 🤖 Agentes CrewAI
│   ├── 🕷️ Web Scraping (Playwright)
│   ├── 🗄️ Banco de Dados (SQLite)
│   └── 🔗 APIs REST
└── 📊 Dados
    ├── 📋 Templates de Editais
    ├── 🧠 Base de Conhecimento
    └── 📈 Histórico de Licitações
```

## 🛠️ Tecnologias Utilizadas

### Backend
- **FastAPI** - Framework web moderno e rápido
- **CrewAI** - Framework para agentes de IA colaborativos
- **Playwright** - Web scraping moderno e confiável
- **SQLAlchemy** - ORM para banco de dados
- **OpenAI GPT** - Modelos de linguagem avançados
- **SQLite** - Banco de dados leve e eficiente

### Frontend
- **React** - Biblioteca para interfaces de usuário
- **React Router** - Roteamento de páginas
- **CSS3** - Estilização moderna e responsiva

### Ferramentas de IA
- **CrewAI Agents** - Agentes especializados
- **OpenAI API** - Processamento de linguagem natural
- **Análise de Padrões** - Machine learning para insights

## 📦 Instalação e Configuração

### 1. Pré-requisitos
```bash
# Python 3.8+
python --version

# Node.js 16+
node --version

# Git
git --version
```

### 2. Configuração do Backend
```bash
# Clonar repositório
git clone <repository-url>
cd licitacao-ai/backend

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Instalar Playwright
python -m playwright install chromium

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas chaves de API
```

### 3. Configuração do Frontend
```bash
cd ../frontend

# Instalar dependências
npm install

# Configurar variáveis de ambiente
cp .env.example .env.local
# Editar .env.local se necessário
```

### 4. Inicialização do Sistema
```bash
# Terminal 1 - Backend
cd backend
python -m uvicorn api.app:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm start

# Terminal 3 - Popular dados iniciais
cd backend
python utils/populate_initial_data.py

# Terminal 4 - Executar scraping inicial
cd backend
python scripts/run_scraping.py
```

## 🎯 Como Usar

### 1. Análise de Licitações
1. Acesse `http://localhost:3000`
2. Clique em "📊 Análise"
3. Use a busca automática ou manual
4. Visualize resultados e análises

### 2. Geração de Editais
1. Acesse `http://localhost:3000/gerar-edital`
2. Preencha dados básicos da licitação
3. Configure requisitos avançados
4. Aguarde processamento automático
5. Revise e baixe o edital gerado

### 3. Base de Conhecimento
1. Acesse `http://localhost:3000/base-conhecimento`
2. **Resumo**: Veja estatísticas gerais
3. **Consultar**: Busque licitações similares
4. **Coletar Dados**: Execute web scraping
5. **Analytics**: Analise tendências

## 🔧 APIs Disponíveis

### Análise de Licitações
- `GET /api/licitacoes` - Listar licitações
- `POST /api/licitacoes/buscar` - Buscar novas licitações
- `POST /api/licitacoes/analisar` - Analisar com IA

### Geração de Editais
- `POST /api/editais/gerar` - Gerar novo edital
- `GET /api/editais/status/{id}` - Verificar status
- `GET /api/editais/{id}` - Obter edital gerado
- `GET /api/editais/templates` - Listar templates

### Base de Conhecimento
- `POST /api/scraping/executar` - Executar web scraping
- `GET /api/scraping/base-conhecimento/consultar` - Consultar base
- `GET /api/scraping/base-conhecimento/analytics` - Analytics
- `POST /api/scraping/agendar` - Agendar coleta automática

## 🧠 Inteligência Artificial

### Agentes CrewAI
Cada agente tem especialização específica:

- **Coletor**: Valida e estrutura requisitos
- **Jurídico**: Garante conformidade legal
- **Técnico**: Analisa viabilidade técnica
- **Financeiro**: Valida aspectos econômicos
- **Risco**: Calcula probabilidades de sucesso
- **Gerador**: Cria conteúdo do edital
- **Otimizador**: Aplica melhorias finais
- **Coordenador**: Gerencia processo completo
- **Conhecimento**: Aplica aprendizados da base

### Base de Conhecimento
- Coleta automática de licitações bem-sucedidas
- Análise de padrões de sucesso
- Recomendações baseadas em dados históricos
- Aprendizado contínuo do sistema

## 📊 Monitoramento e Logs

### Logs do Sistema
```bash
# Backend logs
tail -f backend/logs/app.log

# Scraping logs
tail -f backend/logs/scraping.log

# CrewAI logs
tail -f backend/logs/crewai.log
```

### Métricas Importantes
- Taxa de sucesso de editais gerados
- Tempo médio de processamento
- Qualidade das análises de IA
- Cobertura da base de conhecimento

## 🔒 Segurança

- Validação de entrada em todas as APIs
- Sanitização de dados de web scraping
- Rate limiting para APIs externas
- Logs de auditoria para ações críticas

## 🚀 Próximos Passos

### Melhorias Planejadas
1. **Integração com sistemas dos Correios**
2. **Dashboard executivo com KPIs**
3. **Notificações automáticas**
4. **API para integração externa**
5. **Machine learning avançado**
6. **Análise de sentimento em propostas**

### Escalabilidade
- Migração para PostgreSQL
- Deploy em containers Docker
- Implementação de cache Redis
- Processamento assíncrono com Celery

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique os logs do sistema
2. Consulte a documentação da API
3. Execute testes de conectividade
4. Verifique configurações de ambiente

## 📄 Licença

Sistema desenvolvido para os Correios - Uso interno.

---

**🎉 Sistema completo e funcional para modernizar o processo de licitações dos Correios com inteligência artificial!**
