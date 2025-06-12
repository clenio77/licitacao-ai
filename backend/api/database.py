import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, JSON, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Diretório base do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.abspath(os.path.join(BASE_DIR, '../../data'))
os.makedirs(DATA_DIR, exist_ok=True)
# Caminho do arquivo do banco SQLite3
DB_PATH = os.path.join(DATA_DIR, 'licitacoes.db')
# URL de conexão para o SQLAlchemy
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Cria o engine do SQLAlchemy para SQLite3
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
# Cria a fábrica de sessões para o banco
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base para os modelos ORM
Base = declarative_base()

class Licitacao(Base):
    """
    Modelo de dados para licitações.
    Cada instância representa uma licitação processada pelo sistema.
    Os campos mapeiam as colunas da tabela 'licitacoes' no banco de dados.
    """
    __tablename__ = "licitacoes"

    id = Column(String, primary_key=True, index=True) # ID gerado pelos agentes
    objeto = Column(Text, nullable=False) # Objeto da licitação
    data_abertura = Column(String, nullable=True) # Data de abertura
    prazo_proposta = Column(String, nullable=True) # Prazo para envio de propostas
    valor_estimado = Column(Float, nullable=True) # Valor estimado
    requisito_habilitacao_principal = Column(Text, nullable=True) # Requisito principal
    resumo = Column(Text, nullable=True) # Resumo do edital
    link_original = Column(String, nullable=True) # Link para o edital original
    data_processamento = Column(DateTime, default=datetime.now) # Data de processamento
    status = Column(String, default="processado_mvp") # Status do processamento
    analise_juridica_texto = Column(Text, nullable=True) # Texto da análise jurídica
    pontos_de_atencao_juridica = Column(JSON, nullable=True) # Lista de pontos de atenção jurídica
    analise_mercado_texto = Column(Text, nullable=True) # Texto da análise de mercado
    sugestao_preco_referencia = Column(Float, nullable=True) # Sugestão de preço de referência
    analise_cambial_texto = Column(Text, nullable=True) # Texto da análise cambial
    resumo_executivo_gerencial = Column(Text, nullable=True) # Resumo executivo
    risco_geral = Column(String, nullable=True) # Risco geral (baixo, médio, alto)
    recomendacao_final = Column(Text, nullable=True) # Recomendação final
    ultima_notificacao_risco = Column(DateTime, nullable=True) # Última notificação de risco
    ultima_notificacao_variacao_cambial = Column(DateTime, nullable=True) # Última notificação de variação cambial
    ultima_notificacao_teams_risco = Column(DateTime, nullable=True) # Última notificação Teams
    modalidade = Column(String, nullable=True)
    tipo_licitacao = Column(String, nullable=True)
    numero_edital = Column(String, nullable=True)
    data_publicacao = Column(String, nullable=True)
    uasg = Column(String, nullable=True)
    dependencia = Column(String, nullable=True)
    uf = Column(String, nullable=True)
    quantidade_itens = Column(String, nullable=True)
    nup = Column(String, nullable=True)

    def __repr__(self):
        """
        Retorna uma representação resumida da licitação para debug/log.
        """
        return f"<Licitacao(id='{self.id}', objeto='{self.objeto[:50]}...')>"


def create_db_tables():
    """
    Cria as tabelas do banco de dados se não existirem.
    Deve ser chamada no início da aplicação para garantir a estrutura do banco.
    """
    print("Criando tabelas do banco de dados (se não existirem)...")
    Base.metadata.create_all(bind=engine)
    print("Tabelas verificadas/criadas.")


def get_db():
    """
    Gera uma sessão de banco de dados para uso nos endpoints.
    Deve ser usada com o Depends do FastAPI para garantir abertura e fechamento corretos.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# === NOVOS MODELOS PARA GERAÇÃO DE EDITAIS ===

class EditalRequest(Base):
    """
    Modelo para solicitações de geração de edital.
    Armazena os dados de entrada fornecidos pela equipe de compras.
    """
    __tablename__ = "edital_requests"

    id = Column(String, primary_key=True, index=True)
    objeto = Column(Text, nullable=False)
    tipo_licitacao = Column(String, nullable=False)  # concorrencia, pregao, etc
    modalidade = Column(String, nullable=False)  # presencial, eletronica, hibrida
    categoria = Column(String, nullable=False)  # bens, servicos, obras, etc

    # Dados do setor requisitante (JSON)
    setor_requisitante = Column(JSON, nullable=False)

    # Itens e requisitos (JSON)
    itens = Column(JSON, nullable=False)
    requisitos_tecnicos = Column(JSON, nullable=True)
    requisitos_juridicos = Column(JSON, nullable=True)

    # Valores e prazos
    valor_total_estimado = Column(Float, nullable=True)
    prazo_execucao = Column(Integer, nullable=True)
    prazo_proposta = Column(Integer, default=7)

    # Configurações
    permite_consorcio = Column(Boolean, default=False)
    exige_visita_tecnica = Column(Boolean, default=False)
    criterio_julgamento = Column(String, default="menor_preco")

    # Metadados
    observacoes = Column(Text, nullable=True)
    referencias_editais = Column(JSON, nullable=True)
    data_criacao = Column(DateTime, default=datetime.now)
    criado_por = Column(String, nullable=False)
    status = Column(String, default="pendente")  # pendente, processando, concluido, erro

class EditalGerado(Base):
    """
    Modelo para editais gerados pelo sistema.
    Armazena o resultado completo da geração incluindo análises.
    """
    __tablename__ = "editais_gerados"

    id = Column(String, primary_key=True, index=True)
    numero_edital = Column(String, nullable=True, index=True)
    request_id = Column(String, nullable=False, index=True)  # FK para EditalRequest

    # Análises realizadas (JSON)
    analise_juridica = Column(JSON, nullable=False)
    analise_tecnica = Column(JSON, nullable=False)
    analise_financeira = Column(JSON, nullable=False)
    analise_risco = Column(JSON, nullable=False)

    # Conteúdo do edital
    conteudo_edital = Column(Text, nullable=False)
    anexos = Column(JSON, nullable=True)

    # Metadados
    status = Column(String, default="rascunho")  # rascunho, em_analise, aprovado, publicado, cancelado
    data_criacao = Column(DateTime, default=datetime.now)
    data_modificacao = Column(DateTime, nullable=True)
    criado_por = Column(String, nullable=False)
    versao = Column(Integer, default=1)

    # Histórico e aprendizado
    editais_referencia = Column(JSON, nullable=True)
    melhorias_aplicadas = Column(JSON, nullable=True)

class HistoricoEdital(Base):
    """
    Modelo para histórico de sucessos/fracassos de editais.
    Base de conhecimento para melhorar futuras gerações.
    """
    __tablename__ = "historico_editais"

    id = Column(String, primary_key=True, index=True)
    id_edital = Column(String, nullable=False, index=True)
    objeto = Column(Text, nullable=False)
    categoria = Column(String, nullable=False)
    tipo_licitacao = Column(String, nullable=False)

    # Resultado
    sucesso = Column(Boolean, nullable=False)
    motivo_fracasso = Column(Text, nullable=True)
    licoes_aprendidas = Column(JSON, nullable=True)

    # Dados do resultado
    data_resultado = Column(DateTime, nullable=False)
    valor_contratado = Column(Float, nullable=True)
    numero_propostas = Column(Integer, nullable=True)

    # Análise do fracasso/sucesso
    fatores_sucesso = Column(JSON, nullable=True)
    fatores_fracasso = Column(JSON, nullable=True)

    # Metadados
    data_criacao = Column(DateTime, default=datetime.now)
    criado_por = Column(String, nullable=False)

class TemplateEdital(Base):
    """
    Modelo para templates de editais por categoria.
    Templates base para geração automática.
    """
    __tablename__ = "templates_editais"

    id = Column(String, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    categoria = Column(String, nullable=False, index=True)
    tipo_licitacao = Column(String, nullable=False)

    # Template
    conteudo_template = Column(Text, nullable=False)
    variaveis = Column(JSON, nullable=True)  # Lista de variáveis do template

    # Configurações
    ativo = Column(Boolean, default=True)
    data_criacao = Column(DateTime, default=datetime.now)
    versao = Column(String, default="1.0")
    criado_por = Column(String, nullable=False)

    # Metadados de uso
    vezes_usado = Column(Integer, default=0)
    taxa_sucesso = Column(Float, nullable=True)  # Taxa de sucesso dos editais gerados

if __name__ == "__main__":
    # Exemplo de uso para criar tabelas e testar a conexão
    create_db_tables()