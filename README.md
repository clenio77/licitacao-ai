# Sistema de Gestão de Licitações do Correio (MVP)

Este projeto implementa um Sistema de Gestão de Licitações automatizado para o Correio, utilizando inteligência artificial (CrewAI) para coletar, analisar e gerenciar editais de licitação. O sistema oferece visibilidade em tempo real e notificações proativas sobre riscos e variações cambiais.

## Tecnologias Utilizadas

* **Backend**: Python (FastAPI, CrewAI, Playwright, SQLAlchemy)
* **Banco de Dados**: PostgreSQL
* **Web Scraping**: Playwright
* **Orquestração de Agentes**: CrewAI
* **Modelos de Linguagem**: OpenAI GPT (via API)
* **Notificações**: E-mail (SMTP), Microsoft Teams (Webhooks)
* **Frontend**: React.js

## Estrutura do Projeto

correios_licitacoes_mvp/
├── backend/                  # Código Python (API, Agentes, Scrapers)
│   ├── crewai_agents/        # Definições de Agentes, Tarefas, Ferramentas e o orquestrador principal
│   ├── web_scraping/         # Módulos para coleta de dados (Playwright) e processamento de documentos
│   ├── api/                  # API FastAPI e configurações de Banco de Dados
│   └── data/                 # Arquivos de dados (leis, preços, registros, docs brutos/gerados)
├── frontend/                 # Aplicação React.js
├── .env                      # Variáveis de ambiente (crie este arquivo!)
├── requirements.txt          # Dependências Python
├── docker-compose.yml        # Configuração para o banco de dados PostgreSQL
├── README.md                 # Este arquivo


## Como Iniciar o Projeto

Siga os passos abaixo para configurar e rodar o sistema.

### Pré-requisitos

1.  **Git**: Para clonar o repositório.
2.  **Docker Desktop**: Necessário para rodar o banco de dados PostgreSQL.
3.  **Python 3.9+** e **pip**: Para o backend.
4.  **Node.js e npm** (ou Yarn): Para o frontend React.
5.  **Chave de API OpenAI**: Para os Modelos de Linguagem (LLMs).
6.  **URL de Webhook do Microsoft Teams**: Para notificações no Teams.
7.  **Credenciais de Servidor SMTP**: Para notificações por e-mail.
8.  **Chave de API ExchangeRate-API.com**: Para cotações cambiais (gratuita para uso limitado).

### 1. Clonar o Repositório

```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd correios_licitacoes_mvp
2. Configurar Variáveis de Ambiente
Crie um arquivo chamado .env na raiz do projeto (na mesma pasta deste README.md). Copie o conteúdo de .env.example para .env e preencha com suas credenciais e chaves de API.

Exemplo de .env (preencha com seus dados reais):

# ... (conteúdo do .env acima) ...
Atenção: O arquivo .env contém informações sensíveis e NÃO DEVE ser versionado no Git.

3. Configurar o Backend
Instalar Dependências Python:
Bash

cd backend
pip install -r requirements.txt
Instalar Playwright Browsers:
Bash

playwright install
Preparar Arquivos de Dados:
backend/data/lei_14133_2021.txt: Cole o texto completo da Lei nº 14.133/2021 neste arquivo.
backend/data/precos_referencia.json: Crie e preencha este arquivo com dados de preços de referência, como no exemplo abaixo:
JSON

{
  "servico_limpeza_m2": 15.50,
  "material_escritorio_resma_papel": 35.00,
  "manutencao_predial_hora_tecnico": 120.00,
  "licenca_software_antivirus_unidade": 80.00,
  "computador_desktop_basico": 2800.00
}
backend/data/raw_licitacoes/edital_exemplo_mvp.pdf: Baixe um edital de licitação em PDF (ou DOCX) real do Comprasnet e salve-o com este nome neste caminho. Isso é crucial para o processo de análise e extração de texto.
4. Iniciar o Banco de Dados (PostgreSQL)
Na raiz do projeto (correios_licitacoes_mvp/), execute:

Bash

docker-compose up -d db
Aguarde alguns segundos para o container iniciar.

5. Iniciar o Servidor FastAPI (API Backend)
Em um novo terminal, vá para a pasta backend/ e execute:

Bash

cd backend
uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
A API estará disponível em http://localhost:8000. Ela criará automaticamente as tabelas no PostgreSQL na primeira inicialização.

6. Executar a Crew de Agentes
Em outro novo terminal (diferente do da API), vá para a pasta backend/ e execute:

Bash

cd backend
python crewai_agents/main.py
Este script fará a busca no Comprasnet, processará os editais (incluindo o de exemplo), fará análises jurídicas, de mercado e gerenciais, e salvará os dados no PostgreSQL. Se as condições de risco forem atendidas, ele também enviará notificações para o Teams e/ou e-mail.

7. Configurar e Iniciar o Frontend (React)
Instalar Dependências Node.js:
Bash

cd frontend
npm install
Iniciar o Servidor de Desenvolvimento React:
Bash

npm start
Isso abrirá o aplicativo no seu navegador, geralmente em http://localhost:3000.
8. Visualizar o Sistema
Abra seu navegador e acesse http://localhost:3000. Você verá a interface web exibindo os dados das licitações processadas.

Próximos Passos e Melhorias (Sugestões)
Agora que você tem o sistema rodando, pode considerar as seguintes melhorias:

Robustez do Web Scraping: Aprimorar mcp_playwright.py para lidar com a complexidade e variabilidade do Comprasnet de forma mais robusta.
Geração de Documentos On-Demand: Implementar um endpoint na API para acionar o GeradorDeDocumentos para criar relatórios ou minutas específicas.
Gestão de Status no Frontend: Adicionar funcionalidade na interface para que os usuários possam atualizar manualmente o status de uma licitação (ex: "Em Análise Humana", "Decidido Participar").
Autenticação e Autorização: Proteger a API e o frontend com login de usuários.
Deployment em Produção: Usar ferramentas como Docker Swarm ou Kubernetes para um deployment escalável e resiliente.
Espero que este conjunto de arquivos e instruções o ajude a dar o próximo grande passo com seu 