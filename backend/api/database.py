import os
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, JSON, Boolean, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
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
    # Novos campos para análise ambiental
    analise_ambiental_texto = Column(Text, nullable=True) # Texto da análise ambiental
    impacto_ambiental = Column(String, nullable=True) # baixo, médio, alto
    criterios_sustentabilidade = Column(JSON, nullable=True) # Lista de critérios ambientais
    certificacoes_exigidas = Column(JSON, nullable=True) # Lista de certificações ambientais

    def __repr__(self):
        """
        Retorna uma representação resumida da licitação para debug/log.
        """
        return f"<Licitacao(id='{self.id}', objeto='{self.objeto[:50]}...')>"

class RequisicaoInterna(Base):
    """
    Modelo para requisições internas de licitação dos funcionários.
    """
    __tablename__ = "requisicoes_internas"

    id = Column(String, primary_key=True, index=True)
    numero_requisicao = Column(String, unique=True, index=True)
    
    # Dados do solicitante
    solicitante_nome = Column(String, nullable=False)
    solicitante_email = Column(String, nullable=False)
    solicitante_cargo = Column(String, nullable=True)
    setor_solicitante = Column(String, nullable=False)
    telefone_contato = Column(String, nullable=True)
    
    # Dados da requisição
    tipo_pedido = Column(String, nullable=False) # servico, produto, obra
    objeto = Column(Text, nullable=False) # Descrição do objeto
    justificativa = Column(Text, nullable=False) # Justificativa da necessidade
    valor_estimado = Column(Float, nullable=True)
    prazo_necessidade = Column(DateTime, nullable=True)
    local_execucao = Column(String, nullable=True)
    
    # Especificações técnicas
    especificacoes_tecnicas = Column(Text, nullable=True)
    quantidade = Column(String, nullable=True)
    unidade_medida = Column(String, nullable=True)
    criterios_selecao = Column(JSON, nullable=True)
    
    # Documentação
    documentos_anexos = Column(JSON, nullable=True) # Lista de caminhos dos arquivos
    observacoes = Column(Text, nullable=True)
    
    # Controle de workflow
    status = Column(String, default="pendente") # pendente, em_analise, aprovado, rejeitado, finalizado
    data_criacao = Column(DateTime, default=datetime.now)
    data_atualizacao = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Prioridade e categoria
    prioridade = Column(String, default="normal") # baixa, normal, alta, urgente
    categoria = Column(String, nullable=True) # ti, manutencao, limpeza, etc.
    
    # Relação com aprovações
    aprovacoes = relationship("AprovacaoRequisicao", back_populates="requisicao")
    
    def __repr__(self):
        return f"<RequisicaoInterna(id='{self.id}', objeto='{self.objeto[:50]}...')>"

class AprovacaoRequisicao(Base):
    """
    Modelo para controle de aprovações das requisições.
    """
    __tablename__ = "aprovacoes_requisicao"

    id = Column(String, primary_key=True, index=True)
    requisicao_id = Column(String, ForeignKey("requisicoes_internas.id"), nullable=False)
    
    # Dados do aprovador
    aprovador_nome = Column(String, nullable=False)
    aprovador_email = Column(String, nullable=False)
    aprovador_cargo = Column(String, nullable=True)
    nivel_aprovacao = Column(String, nullable=False) # supervisor, compras, orcamento, final
    
    # Decisão
    decisao = Column(String, nullable=False) # aprovado, rejeitado, solicitado_alteracao
    data_decisao = Column(DateTime, default=datetime.now)
    comentarios = Column(Text, nullable=True)
    
    # Controle de workflow
    ordem_aprovacao = Column(Integer, nullable=False) # Ordem na sequência de aprovação
    status = Column(String, default="pendente") # pendente, processado
    
    # Relação com requisição
    requisicao = relationship("RequisicaoInterna", back_populates="aprovacoes")
    
    def __repr__(self):
        return f"<AprovacaoRequisicao(id='{self.id}', nivel='{self.nivel_aprovacao}')>"

class WorkflowStatus(Base):
    """
    Modelo para rastreamento do status do workflow.
    """
    __tablename__ = "workflow_status"

    id = Column(String, primary_key=True, index=True)
    requisicao_id = Column(String, ForeignKey("requisicoes_internas.id"), nullable=False)
    
    # Status atual
    etapa_atual = Column(String, nullable=False) # criada, supervisor, compras, orcamento, analise_ia, finalizada
    status_etapa = Column(String, nullable=False) # pendente, em_andamento, concluida, rejeitada
    
    # Dados da etapa
    data_inicio = Column(DateTime, default=datetime.now)
    data_conclusao = Column(DateTime, nullable=True)
    responsavel_atual = Column(String, nullable=True)
    
    # Observações
    observacoes = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<WorkflowStatus(id='{self.id}', etapa='{self.etapa_atual}')>"

class AnaliseAmbiental(Base):
    """
    Modelo para análises ambientais das licitações.
    """
    __tablename__ = "analises_ambientais"

    id = Column(String, primary_key=True, index=True)
    licitacao_id = Column(String, nullable=True) # Pode ser vinculada a licitação existente
    requisicao_id = Column(String, ForeignKey("requisicoes_internas.id"), nullable=True) # Ou a requisição interna
    
    # Análise ambiental
    impacto_ambiental = Column(String, nullable=False) # baixo, médio, alto
    legislacao_aplicavel = Column(JSON, nullable=True) # Lista de leis e normas
    criterios_sustentabilidade = Column(JSON, nullable=True) # Lista de critérios
    certificacoes_exigidas = Column(JSON, nullable=True) # Lista de certificações
    
    # Textos da análise
    analise_detalhada = Column(Text, nullable=True)
    recomendacoes = Column(Text, nullable=True)
    riscos_identificados = Column(JSON, nullable=True)
    
    # Controle
    data_analise = Column(DateTime, default=datetime.now)
    analista_responsavel = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<AnaliseAmbiental(id='{self.id}', impacto='{self.impacto_ambiental}')>"

# Modelos existentes para editais (mantidos para compatibilidade)
class EditalRequest(Base):
    """Modelo para solicitações de edital."""
    __tablename__ = "edital_requests"

    id = Column(String, primary_key=True, index=True)
    objeto = Column(Text, nullable=False)
    tipo_licitacao = Column(String, nullable=False)
    modalidade = Column(String, nullable=False)
    categoria = Column(String, nullable=False)
    setor_requisitante = Column(String, nullable=False)
    itens = Column(JSON, nullable=False)
    requisitos_tecnicos = Column(JSON, nullable=True)
    requisitos_juridicos = Column(JSON, nullable=True)
    valor_total_estimado = Column(Float, nullable=True)
    prazo_execucao = Column(String, nullable=True)
    prazo_proposta = Column(Integer, default=7)
    permite_consorcio = Column(Boolean, default=False)
    exige_visita_tecnica = Column(Boolean, default=False)
    criterio_julgamento = Column(String, default="menor_preco")
    observacoes = Column(Text, nullable=True)
    referencias_editais = Column(JSON, nullable=True)
    criado_por = Column(String, nullable=False)
    data_criacao = Column(DateTime, default=datetime.now)
    status = Column(String, default="pendente")

class EditalGerado(Base):
    """Modelo para editais gerados."""
    __tablename__ = "editais_gerados"

    id = Column(String, primary_key=True, index=True)
    numero_edital = Column(String, unique=True, index=True)
    request_id = Column(String, ForeignKey("edital_requests.id"), nullable=False)
    conteudo_edital = Column(Text, nullable=False)
    status = Column(String, default="rascunho")
    data_criacao = Column(DateTime, default=datetime.now)
    data_modificacao = Column(DateTime, nullable=True)
    criado_por = Column(String, nullable=False)
    versao = Column(Integer, default=1)
    analise_juridica = Column(Text, nullable=True)
    analise_tecnica = Column(Text, nullable=True)
    analise_financeira = Column(Text, nullable=True)
    analise_risco = Column(Text, nullable=True)
    anexos = Column(JSON, nullable=True)
    editais_referencia = Column(JSON, nullable=True)
    melhorias_aplicadas = Column(JSON, nullable=True)

class HistoricoEdital(Base):
    """Modelo para histórico de editais."""
    __tablename__ = "historico_editais"

    id = Column(String, primary_key=True, index=True)
    id_edital = Column(String, ForeignKey("editais_gerados.id"), nullable=False)
    objeto = Column(Text, nullable=False)
    categoria = Column(String, nullable=False)
    tipo_licitacao = Column(String, nullable=False)
    sucesso = Column(Boolean, nullable=False)
    motivo_fracasso = Column(Text, nullable=True)
    licoes_aprendidas = Column(JSON, nullable=True)
    data_resultado = Column(DateTime, nullable=False)
    valor_contratado = Column(Float, nullable=True)
    numero_propostas = Column(Integer, nullable=True)
    criado_por = Column(String, nullable=False)

class TemplateEdital(Base):
    """Modelo para templates de editais."""
    __tablename__ = "templates_editais"

    id = Column(String, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    categoria = Column(String, nullable=False)
    tipo_licitacao = Column(String, nullable=False)
    conteudo_template = Column(Text, nullable=False)
    variaveis_template = Column(JSON, nullable=True)
    versao = Column(Integer, default=1)
    ativo = Column(Boolean, default=True)
    vezes_usado = Column(Integer, default=0)
    taxa_sucesso = Column(Float, nullable=True)
    data_criacao = Column(DateTime, default=datetime.now)
    criado_por = Column(String, nullable=False)

def create_db_tables():
    """
    Cria todas as tabelas no banco de dados se elas não existirem.
    """
    Base.metadata.create_all(bind=engine)
    print("Tabelas do banco de dados criadas/verificadas com sucesso.")

def get_db():
    """
    Função para obter sessão do banco de dados.
    Usada como dependência no FastAPI.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    create_db_tables()
    print("Banco de dados configurado com sucesso!")