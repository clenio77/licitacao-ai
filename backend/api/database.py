import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, JSON
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Diretório base do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Caminho do arquivo do banco SQLite3
DB_PATH = os.path.join(BASE_DIR, '../../data/licitacoes.db')
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

if __name__ == "__main__":
    # Exemplo de uso para criar tabelas e testar a conexão
    create_db_tables()