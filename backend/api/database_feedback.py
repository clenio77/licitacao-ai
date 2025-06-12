"""
Modelos de banco de dados para sistema de feedback e melhoria contínua.
Coleta opiniões de setores requisitantes, empresas licitantes e setor de licitação.
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class FeedbackSetor(Base):
    """
    Feedback dos setores requisitantes sobre o processo de geração de editais.
    """
    __tablename__ = "feedback_setor"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    edital_id = Column(String, ForeignKey("edital_gerado.id"), nullable=False)
    
    # Dados do setor
    setor_nome = Column(String, nullable=False)
    responsavel_nome = Column(String, nullable=False)
    responsavel_email = Column(String, nullable=False)
    responsavel_cargo = Column(String)
    
    # Avaliações (1-5)
    facilidade_uso = Column(Integer)  # Quão fácil foi usar o sistema
    qualidade_edital = Column(Integer)  # Qualidade do edital gerado
    adequacao_requisitos = Column(Integer)  # Edital atendeu aos requisitos
    tempo_processamento = Column(Integer)  # Satisfação com tempo
    clareza_especificacoes = Column(Integer)  # Clareza das especificações
    
    # Feedback qualitativo
    pontos_positivos = Column(Text)
    pontos_negativos = Column(Text)
    sugestoes_melhoria = Column(Text)
    problemas_encontrados = Column(Text)
    
    # Comparação com processo manual
    preferencia_sistema = Column(Boolean)  # Prefere sistema automatizado
    economia_tempo_estimada = Column(Integer)  # % de tempo economizado
    
    # Dados específicos
    areas_melhorar = Column(JSON)  # Lista de áreas que precisam melhorar
    funcionalidades_desejadas = Column(JSON)  # Novas funcionalidades desejadas
    
    # Metadados
    data_feedback = Column(DateTime, default=datetime.now)
    ip_origem = Column(String)
    user_agent = Column(String)
    
    # Relacionamento
    edital = relationship("EditalGerado", back_populates="feedbacks_setor")

class FeedbackEmpresa(Base):
    """
    Feedback das empresas licitantes sobre a qualidade dos editais.
    """
    __tablename__ = "feedback_empresa"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    edital_id = Column(String, ForeignKey("edital_gerado.id"), nullable=False)
    
    # Dados da empresa
    empresa_cnpj = Column(String, nullable=False)
    empresa_nome = Column(String, nullable=False)
    empresa_porte = Column(String)  # micro, pequena, media, grande
    empresa_segmento = Column(String)
    respondente_nome = Column(String)
    respondente_cargo = Column(String)
    respondente_email = Column(String)
    
    # Participação na licitação
    participou_licitacao = Column(Boolean, nullable=False)
    motivo_nao_participacao = Column(Text)  # Se não participou, por quê?
    
    # Avaliações do edital (1-5)
    clareza_objeto = Column(Integer)  # Clareza na descrição do objeto
    adequacao_especificacoes = Column(Integer)  # Especificações técnicas adequadas
    prazo_elaboracao_proposta = Column(Integer)  # Prazo suficiente
    criterios_julgamento = Column(Integer)  # Critérios claros e justos
    exigencias_habilitacao = Column(Integer)  # Exigências proporcionais
    valor_estimado = Column(Integer)  # Valor compatível com mercado
    
    # Feedback sobre competitividade
    nivel_competitividade = Column(Integer)  # 1=baixa, 5=alta
    barreiras_participacao = Column(JSON)  # Lista de barreiras identificadas
    
    # Feedback qualitativo
    aspectos_positivos = Column(Text)
    aspectos_negativos = Column(Text)
    sugestoes_especificas = Column(Text)
    comparacao_outros_editais = Column(Text)
    
    # Impacto no negócio
    interesse_futuras_licitacoes = Column(Boolean)
    recomendaria_outros_fornecedores = Column(Boolean)
    
    # Metadados
    data_feedback = Column(DateTime, default=datetime.now)
    forma_coleta = Column(String)  # email, formulario, telefone, presencial
    
    # Relacionamento
    edital = relationship("EditalGerado", back_populates="feedbacks_empresa")

class FeedbackLicitacao(Base):
    """
    Feedback do setor de licitação sobre o processo e resultados.
    """
    __tablename__ = "feedback_licitacao"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    edital_id = Column(String, ForeignKey("edital_gerado.id"), nullable=False)
    
    # Dados do avaliador
    avaliador_nome = Column(String, nullable=False)
    avaliador_cargo = Column(String, nullable=False)
    avaliador_experiencia = Column(Integer)  # Anos de experiência
    
    # Avaliação do processo (1-5)
    qualidade_tecnica = Column(Integer)  # Qualidade técnica do edital
    conformidade_legal = Column(Integer)  # Conformidade com legislação
    adequacao_modalidade = Column(Integer)  # Modalidade adequada
    clareza_redacao = Column(Integer)  # Clareza na redação
    completude_documentos = Column(Integer)  # Documentos completos
    
    # Resultados da licitação
    numero_propostas_recebidas = Column(Integer)
    numero_empresas_habilitadas = Column(Integer)
    houve_impugnacoes = Column(Boolean)
    numero_impugnacoes = Column(Integer)
    principais_questionamentos = Column(JSON)
    
    # Processo licitatório
    tempo_analise_propostas = Column(Float)  # Horas para analisar
    complexidade_julgamento = Column(Integer)  # 1=simples, 5=complexo
    necessidade_esclarecimentos = Column(Boolean)
    
    # Comparação com editais manuais
    qualidade_vs_manual = Column(Integer)  # 1=pior, 3=igual, 5=melhor
    tempo_vs_manual = Column(Integer)  # 1=mais lento, 3=igual, 5=mais rápido
    
    # Feedback específico
    pontos_fortes = Column(Text)
    areas_melhoria = Column(Text)
    erros_identificados = Column(Text)
    sugestoes_tecnicas = Column(Text)
    
    # Impacto operacional
    reducao_retrabalho = Column(Boolean)
    melhoria_padronizacao = Column(Boolean)
    facilidade_acompanhamento = Column(Boolean)
    
    # Metadados
    data_feedback = Column(DateTime, default=datetime.now)
    fase_licitacao = Column(String)  # preparacao, publicacao, julgamento, homologacao
    
    # Relacionamento
    edital = relationship("EditalGerado", back_populates="feedbacks_licitacao")

class SessaoFeedback(Base):
    """
    Sessões de feedback coletivo (workshops, reuniões, grupos focais).
    """
    __tablename__ = "sessao_feedback"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Dados da sessão
    tipo_sessao = Column(String, nullable=False)  # workshop, reuniao, grupo_focal
    titulo = Column(String, nullable=False)
    descricao = Column(Text)
    data_sessao = Column(DateTime, nullable=False)
    duracao_minutos = Column(Integer)
    local_sessao = Column(String)
    modalidade = Column(String)  # presencial, virtual, hibrida
    
    # Participantes
    numero_participantes = Column(Integer)
    perfis_participantes = Column(JSON)  # Lista de perfis dos participantes
    
    # Facilitação
    facilitador_nome = Column(String)
    facilitador_cargo = Column(String)
    metodologia_utilizada = Column(String)
    
    # Resultados
    principais_insights = Column(JSON)  # Lista de insights principais
    problemas_identificados = Column(JSON)  # Lista de problemas
    solucoes_propostas = Column(JSON)  # Lista de soluções
    consensos_alcancados = Column(JSON)  # Lista de consensos
    divergencias = Column(JSON)  # Lista de divergências
    
    # Priorização
    melhorias_prioritarias = Column(JSON)  # Lista priorizada de melhorias
    impacto_estimado = Column(JSON)  # Impacto estimado de cada melhoria
    
    # Documentação
    ata_reuniao = Column(Text)
    gravacao_disponivel = Column(Boolean)
    materiais_utilizados = Column(JSON)
    
    # Follow-up
    acoes_definidas = Column(JSON)  # Lista de ações com responsáveis
    prazo_implementacao = Column(JSON)  # Prazos para cada ação
    proxima_sessao = Column(DateTime)
    
    # Metadados
    data_criacao = Column(DateTime, default=datetime.now)
    criado_por = Column(String)
    status = Column(String, default="planejada")  # planejada, realizada, cancelada

class AnaliseImpacto(Base):
    """
    Análise de impacto das melhorias implementadas baseadas em feedback.
    """
    __tablename__ = "analise_impacto"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Melhoria implementada
    titulo_melhoria = Column(String, nullable=False)
    descricao_melhoria = Column(Text, nullable=False)
    categoria_melhoria = Column(String)  # interface, algoritmo, processo, template
    data_implementacao = Column(DateTime, nullable=False)
    
    # Origem do feedback
    fonte_feedback = Column(String)  # setor, empresa, licitacao, sessao
    feedback_ids = Column(JSON)  # IDs dos feedbacks que geraram a melhoria
    
    # Métricas antes da melhoria
    metricas_antes = Column(JSON)
    periodo_medicao_antes = Column(String)
    
    # Métricas depois da melhoria
    metricas_depois = Column(JSON)
    periodo_medicao_depois = Column(String)
    
    # Impacto calculado
    impacto_quantitativo = Column(JSON)  # Métricas numéricas de impacto
    impacto_qualitativo = Column(Text)  # Descrição qualitativa
    
    # Satisfação dos stakeholders
    satisfacao_setores = Column(Float)  # Média de satisfação dos setores
    satisfacao_empresas = Column(Float)  # Média de satisfação das empresas
    satisfacao_licitacao = Column(Float)  # Média de satisfação do setor licitação
    
    # ROI e benefícios
    custo_implementacao = Column(Float)
    beneficio_estimado = Column(Float)
    roi_calculado = Column(Float)
    tempo_retorno = Column(Integer)  # Meses para retorno do investimento
    
    # Status e acompanhamento
    status_implementacao = Column(String, default="implementada")
    necessita_ajustes = Column(Boolean, default=False)
    proximos_passos = Column(Text)
    
    # Metadados
    data_analise = Column(DateTime, default=datetime.now)
    analisado_por = Column(String)
    aprovado_por = Column(String)

class ConfiguracaoFeedback(Base):
    """
    Configurações do sistema de feedback.
    """
    __tablename__ = "configuracao_feedback"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Configurações de coleta
    feedback_setor_ativo = Column(Boolean, default=True)
    feedback_empresa_ativo = Column(Boolean, default=True)
    feedback_licitacao_ativo = Column(Boolean, default=True)
    
    # Timing de coleta
    dias_apos_geracao_setor = Column(Integer, default=7)  # Dias após geração para coletar feedback do setor
    dias_apos_publicacao_empresa = Column(Integer, default=30)  # Dias após publicação para empresas
    dias_apos_resultado_licitacao = Column(Integer, default=15)  # Dias após resultado para setor licitação
    
    # Lembretes automáticos
    enviar_lembretes = Column(Boolean, default=True)
    intervalo_lembretes = Column(Integer, default=7)  # Dias entre lembretes
    maximo_lembretes = Column(Integer, default=3)
    
    # Incentivos
    usar_incentivos = Column(Boolean, default=True)
    tipos_incentivos = Column(JSON)  # Lista de tipos de incentivos
    
    # Análise automática
    analise_automatica_ativa = Column(Boolean, default=True)
    frequencia_analise = Column(String, default="mensal")  # diaria, semanal, mensal
    
    # Notificações
    notificar_feedback_recebido = Column(Boolean, default=True)
    notificar_insights_gerados = Column(Boolean, default=True)
    emails_notificacao = Column(JSON)  # Lista de emails para notificações
    
    # Metadados
    data_criacao = Column(DateTime, default=datetime.now)
    data_modificacao = Column(DateTime, default=datetime.now)
    modificado_por = Column(String)

# Adicionar relacionamentos aos modelos existentes
def add_feedback_relationships():
    """Adiciona relacionamentos de feedback aos modelos existentes"""
    from api.database import EditalGerado
    
    # Adicionar relacionamentos ao EditalGerado
    EditalGerado.feedbacks_setor = relationship("FeedbackSetor", back_populates="edital")
    EditalGerado.feedbacks_empresa = relationship("FeedbackEmpresa", back_populates="edital")
    EditalGerado.feedbacks_licitacao = relationship("FeedbackLicitacao", back_populates="edital")
