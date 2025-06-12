"""
Modelos Pydantic para o sistema de geração de editais de licitação.
Define as estruturas de dados para entrada, processamento e saída do sistema.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class TipoLicitacao(str, Enum):
    """Tipos de licitação conforme Lei 14.133/2021"""
    CONCORRENCIA = "concorrencia"
    PREGAO = "pregao"
    CONCURSO = "concurso"
    LEILAO = "leilao"
    DIALOGO_COMPETITIVO = "dialogo_competitivo"

class ModalidadeLicitacao(str, Enum):
    """Modalidades de licitação"""
    PRESENCIAL = "presencial"
    ELETRONICA = "eletronica"
    HIBRIDA = "hibrida"

class CategoriaObjeto(str, Enum):
    """Categorias de objetos licitados"""
    BENS = "bens"
    SERVICOS = "servicos"
    OBRAS = "obras"
    SERVICOS_ENGENHARIA = "servicos_engenharia"

class NivelRisco(str, Enum):
    """Níveis de risco para licitações"""
    BAIXO = "baixo"
    MEDIO = "medio"
    ALTO = "alto"
    CRITICO = "critico"

class StatusEdital(str, Enum):
    """Status do edital no sistema"""
    RASCUNHO = "rascunho"
    EM_ANALISE = "em_analise"
    APROVADO = "aprovado"
    PUBLICADO = "publicado"
    CANCELADO = "cancelado"

# === MODELOS DE ENTRADA ===

class SetorRequisitante(BaseModel):
    """Dados do setor que está solicitando a licitação"""
    nome: str = Field(..., description="Nome do setor requisitante")
    codigo: Optional[str] = Field(None, description="Código do setor")
    responsavel: str = Field(..., description="Nome do responsável")
    email: str = Field(..., description="Email do responsável")
    telefone: Optional[str] = Field(None, description="Telefone de contato")
    justificativa: str = Field(..., description="Justificativa da necessidade")

class RequisitoTecnico(BaseModel):
    """Requisito técnico específico do objeto"""
    descricao: str = Field(..., description="Descrição do requisito")
    obrigatorio: bool = Field(True, description="Se é obrigatório ou desejável")
    criterio_avaliacao: Optional[str] = Field(None, description="Como será avaliado")
    peso: Optional[float] = Field(None, description="Peso na avaliação (0-10)")

class RequisitoJuridico(BaseModel):
    """Requisito jurídico ou legal"""
    descricao: str = Field(..., description="Descrição do requisito")
    base_legal: str = Field(..., description="Base legal (lei, decreto, etc)")
    obrigatorio: bool = Field(True, description="Se é obrigatório")
    documentacao_necessaria: Optional[List[str]] = Field(None, description="Documentos necessários")

class ItemLicitacao(BaseModel):
    """Item individual da licitação"""
    numero: int = Field(..., description="Número do item")
    descricao: str = Field(..., description="Descrição detalhada")
    unidade: str = Field(..., description="Unidade de medida")
    quantidade: float = Field(..., description="Quantidade solicitada")
    valor_estimado_unitario: Optional[float] = Field(None, description="Valor estimado unitário")
    especificacoes_tecnicas: List[RequisitoTecnico] = Field(default_factory=list)
    categoria: CategoriaObjeto = Field(..., description="Categoria do item")

class EditalRequest(BaseModel):
    """Solicitação para geração de edital"""
    # Dados básicos
    objeto: str = Field(..., description="Objeto da licitação")
    tipo_licitacao: TipoLicitacao = Field(..., description="Tipo de licitação")
    modalidade: ModalidadeLicitacao = Field(..., description="Modalidade")
    categoria: CategoriaObjeto = Field(..., description="Categoria principal")
    
    # Setor requisitante
    setor_requisitante: SetorRequisitante = Field(..., description="Dados do setor")
    
    # Itens e requisitos
    itens: List[ItemLicitacao] = Field(..., description="Itens da licitação")
    requisitos_tecnicos: List[RequisitoTecnico] = Field(default_factory=list)
    requisitos_juridicos: List[RequisitoJuridico] = Field(default_factory=list)
    
    # Valores e prazos
    valor_total_estimado: Optional[float] = Field(None, description="Valor total estimado")
    prazo_execucao: Optional[int] = Field(None, description="Prazo de execução em dias")
    prazo_proposta: Optional[int] = Field(7, description="Prazo para apresentação de propostas")
    
    # Configurações específicas
    permite_consorcio: bool = Field(False, description="Permite participação de consórcios")
    exige_visita_tecnica: bool = Field(False, description="Exige visita técnica")
    criterio_julgamento: str = Field("menor_preco", description="Critério de julgamento")
    
    # Observações
    observacoes: Optional[str] = Field(None, description="Observações adicionais")
    referencias_editais: Optional[List[str]] = Field(None, description="IDs de editais de referência")

# === MODELOS DE PROCESSAMENTO ===

class AnaliseJuridica(BaseModel):
    """Resultado da análise jurídica"""
    conforme: bool = Field(..., description="Se está conforme à legislação")
    pontos_atencao: List[str] = Field(default_factory=list)
    sugestoes_melhoria: List[str] = Field(default_factory=list)
    base_legal_aplicavel: List[str] = Field(default_factory=list)
    risco_juridico: NivelRisco = Field(..., description="Nível de risco jurídico")
    observacoes: Optional[str] = Field(None)

class AnaliseTecnica(BaseModel):
    """Resultado da análise técnica"""
    viabilidade: bool = Field(..., description="Se é tecnicamente viável")
    especificacoes_adequadas: bool = Field(..., description="Se as especificações estão adequadas")
    pontos_atencao: List[str] = Field(default_factory=list)
    sugestoes_melhoria: List[str] = Field(default_factory=list)
    risco_tecnico: NivelRisco = Field(..., description="Nível de risco técnico")
    observacoes: Optional[str] = Field(None)

class AnaliseFinanceira(BaseModel):
    """Resultado da análise financeira"""
    orcamento_adequado: bool = Field(..., description="Se o orçamento está adequado")
    valor_mercado_min: Optional[float] = Field(None, description="Valor mínimo de mercado")
    valor_mercado_max: Optional[float] = Field(None, description="Valor máximo de mercado")
    valor_sugerido: Optional[float] = Field(None, description="Valor sugerido")
    fontes_pesquisa: List[str] = Field(default_factory=list)
    risco_financeiro: NivelRisco = Field(..., description="Nível de risco financeiro")
    observacoes: Optional[str] = Field(None)

class AnaliseRisco(BaseModel):
    """Análise consolidada de riscos"""
    risco_geral: NivelRisco = Field(..., description="Risco geral consolidado")
    fatores_risco: List[str] = Field(default_factory=list)
    medidas_mitigacao: List[str] = Field(default_factory=list)
    probabilidade_sucesso: float = Field(..., description="Probabilidade de sucesso (0-1)")
    recomendacao: str = Field(..., description="Recomendação final")

# === MODELOS DE SAÍDA ===

class EditalGerado(BaseModel):
    """Edital gerado pelo sistema"""
    id: str = Field(..., description="ID único do edital")
    numero_edital: Optional[str] = Field(None, description="Número oficial do edital")
    
    # Dados da solicitação original
    request_data: EditalRequest = Field(..., description="Dados da solicitação")
    
    # Análises realizadas
    analise_juridica: AnaliseJuridica = Field(..., description="Análise jurídica")
    analise_tecnica: AnaliseTecnica = Field(..., description="Análise técnica")
    analise_financeira: AnaliseFinanceira = Field(..., description="Análise financeira")
    analise_risco: AnaliseRisco = Field(..., description="Análise de risco")
    
    # Conteúdo do edital
    conteudo_edital: str = Field(..., description="Texto completo do edital")
    anexos: Optional[List[str]] = Field(None, description="Lista de anexos")
    
    # Metadados
    status: StatusEdital = Field(StatusEdital.RASCUNHO, description="Status atual")
    data_criacao: datetime = Field(default_factory=datetime.now)
    data_modificacao: Optional[datetime] = Field(None)
    criado_por: str = Field(..., description="Usuário que criou")
    versao: int = Field(1, description="Versão do edital")
    
    # Histórico e aprendizado
    editais_referencia: Optional[List[str]] = Field(None, description="Editais usados como referência")
    melhorias_aplicadas: Optional[List[str]] = Field(None, description="Melhorias aplicadas baseadas no histórico")

class EditalResponse(EditalGerado):
    """Resposta da API para edital gerado"""
    class Config:
        from_attributes = True

class HistoricoEdital(BaseModel):
    """Histórico de sucesso/fracasso de editais"""
    id_edital: str = Field(..., description="ID do edital")
    objeto: str = Field(..., description="Objeto da licitação")
    categoria: CategoriaObjeto = Field(..., description="Categoria")
    sucesso: bool = Field(..., description="Se foi bem-sucedido")
    motivo_fracasso: Optional[str] = Field(None, description="Motivo do fracasso se aplicável")
    licoes_aprendidas: List[str] = Field(default_factory=list)
    data_resultado: datetime = Field(..., description="Data do resultado")
    valor_contratado: Optional[float] = Field(None, description="Valor final contratado")
    numero_propostas: Optional[int] = Field(None, description="Número de propostas recebidas")

# === MODELOS DE CONFIGURAÇÃO ===

class TemplateEdital(BaseModel):
    """Template de edital por categoria"""
    id: str = Field(..., description="ID do template")
    nome: str = Field(..., description="Nome do template")
    categoria: CategoriaObjeto = Field(..., description="Categoria aplicável")
    tipo_licitacao: TipoLicitacao = Field(..., description="Tipo de licitação")
    conteudo_template: str = Field(..., description="Template do edital")
    variaveis: List[str] = Field(default_factory=list, description="Variáveis do template")
    ativo: bool = Field(True, description="Se está ativo")
    data_criacao: datetime = Field(default_factory=datetime.now)
    versao: str = Field("1.0", description="Versão do template")
