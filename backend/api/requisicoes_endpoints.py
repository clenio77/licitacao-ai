"""
API para requisições internas de licitação.
Gerencia o fluxo completo desde a criação até a aprovação final.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr
import uuid
import json
import os

from api.database import get_db, RequisicaoInterna, AprovacaoRequisicao, WorkflowStatus, AnaliseAmbiental
from crewai_agents.requisicao_main import run_requisicao_analysis_crew

# Router para endpoints de requisições
router = APIRouter(prefix="/api/requisicoes", tags=["Requisições Internas"])

# Modelos Pydantic para requests
class RequisicaoInternaRequest(BaseModel):
    # Dados do solicitante
    solicitante_nome: str
    solicitante_email: EmailStr
    solicitante_cargo: Optional[str] = None
    setor_solicitante: str
    telefone_contato: Optional[str] = None
    
    # Dados da requisição
    tipo_pedido: str  # servico, produto, obra
    objeto: str
    justificativa: str
    valor_estimado: Optional[float] = None
    prazo_necessidade: Optional[datetime] = None
    local_execucao: Optional[str] = None
    
    # Especificações técnicas
    especificacoes_tecnicas: Optional[str] = None
    quantidade: Optional[str] = None
    unidade_medida: Optional[str] = None
    criterios_selecao: Optional[List[str]] = []
    
    # Observações
    observacoes: Optional[str] = None
    prioridade: Optional[str] = "normal"
    categoria: Optional[str] = None

class AprovacaoRequest(BaseModel):
    decisao: str  # aprovado, rejeitado, solicitado_alteracao
    comentarios: Optional[str] = None
    aprovador_nome: str
    aprovador_email: EmailStr
    aprovador_cargo: Optional[str] = None

class RequisicaoResponse(BaseModel):
    id: str
    numero_requisicao: str
    objeto: str
    tipo_pedido: str
    status: str
    prioridade: str
    data_criacao: datetime
    solicitante_nome: str
    setor_solicitante: str
    valor_estimado: Optional[float]
    
    class Config:
        from_attributes = True

@router.post("/", response_model=dict)
def criar_requisicao(
    request: RequisicaoInternaRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Cria uma nova requisição interna de licitação.
    
    Args:
        request: Dados da requisição
        background_tasks: Para processamento em background
        db: Sessão do banco de dados
    
    Returns:
        dict: Informações da requisição criada
    """
    try:
        # Gerar ID único e número de requisição
        requisicao_id = str(uuid.uuid4())
        numero_requisicao = f"REQ-{datetime.now().strftime('%Y%m%d')}-{requisicao_id[:8].upper()}"
        
        # Criar requisição
        requisicao = RequisicaoInterna(
            id=requisicao_id,
            numero_requisicao=numero_requisicao,
            solicitante_nome=request.solicitante_nome,
            solicitante_email=request.solicitante_email,
            solicitante_cargo=request.solicitante_cargo,
            setor_solicitante=request.setor_solicitante,
            telefone_contato=request.telefone_contato,
            tipo_pedido=request.tipo_pedido,
            objeto=request.objeto,
            justificativa=request.justificativa,
            valor_estimado=request.valor_estimado,
            prazo_necessidade=request.prazo_necessidade,
            local_execucao=request.local_execucao,
            especificacoes_tecnicas=request.especificacoes_tecnicas,
            quantidade=request.quantidade,
            unidade_medida=request.unidade_medida,
            criterios_selecao=request.criterios_selecao,
            observacoes=request.observacoes,
            prioridade=request.prioridade,
            categoria=request.categoria,
            status="pendente"
        )
        
        db.add(requisicao)
        
        # Criar status inicial do workflow
        workflow_status = WorkflowStatus(
            id=str(uuid.uuid4()),
            requisicao_id=requisicao_id,
            etapa_atual="criada",
            status_etapa="concluida",
            data_conclusao=datetime.now()
        )
        
        db.add(workflow_status)
        db.commit()
        
        # Iniciar processo de análise em background
        background_tasks.add_task(
            iniciar_workflow_aprovacao,
            requisicao_id
        )
        
        return {
            "sucesso": True,
            "requisicao_id": requisicao_id,
            "numero_requisicao": numero_requisicao,
            "status": "pendente",
            "mensagem": "Requisição criada com sucesso. O processo de aprovação foi iniciado.",
            "data_criacao": datetime.now().isoformat()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar requisição: {str(e)}")

@router.get("/", response_model=List[RequisicaoResponse])
def listar_requisicoes(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    setor: Optional[str] = None,
    prioridade: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Lista requisições com filtros opcionais.
    
    Args:
        skip: Registros a pular (paginação)
        limit: Limite de registros
        status: Filtro por status
        setor: Filtro por setor
        prioridade: Filtro por prioridade
        db: Sessão do banco de dados
    
    Returns:
        List[RequisicaoResponse]: Lista de requisições
    """
    query = db.query(RequisicaoInterna)
    
    if status:
        query = query.filter(RequisicaoInterna.status == status)
    if setor:
        query = query.filter(RequisicaoInterna.setor_solicitante == setor)
    if prioridade:
        query = query.filter(RequisicaoInterna.prioridade == prioridade)
    
    requisicoes = query.offset(skip).limit(limit).all()
    
    return [
        RequisicaoResponse(
            id=req.id,
            numero_requisicao=req.numero_requisicao,
            objeto=req.objeto,
            tipo_pedido=req.tipo_pedido,
            status=req.status,
            prioridade=req.prioridade,
            data_criacao=req.data_criacao,
            solicitante_nome=req.solicitante_nome,
            setor_solicitante=req.setor_solicitante,
            valor_estimado=req.valor_estimado
        )
        for req in requisicoes
    ]

@router.get("/{requisicao_id}", response_model=dict)
def obter_requisicao(requisicao_id: str, db: Session = Depends(get_db)):
    """
    Obtém uma requisição específica pelo ID.
    
    Args:
        requisicao_id: ID da requisição
        db: Sessão do banco de dados
    
    Returns:
        dict: Dados completos da requisição
    """
    requisicao = db.query(RequisicaoInterna).filter(RequisicaoInterna.id == requisicao_id).first()
    
    if not requisicao:
        raise HTTPException(status_code=404, detail="Requisição não encontrada")
    
    # Buscar aprovações
    aprovacoes = db.query(AprovacaoRequisicao).filter(
        AprovacaoRequisicao.requisicao_id == requisicao_id
    ).order_by(AprovacaoRequisicao.ordem_aprovacao).all()
    
    # Buscar workflow status
    workflow_status = db.query(WorkflowStatus).filter(
        WorkflowStatus.requisicao_id == requisicao_id
    ).order_by(WorkflowStatus.data_inicio.desc()).first()
    
    # Buscar análise ambiental se existir
    analise_ambiental = db.query(AnaliseAmbiental).filter(
        AnaliseAmbiental.requisicao_id == requisicao_id
    ).first()
    
    return {
        "id": requisicao.id,
        "numero_requisicao": requisicao.numero_requisicao,
        "solicitante": {
            "nome": requisicao.solicitante_nome,
            "email": requisicao.solicitante_email,
            "cargo": requisicao.solicitante_cargo,
            "setor": requisicao.setor_solicitante,
            "telefone": requisicao.telefone_contato
        },
        "dados_requisicao": {
            "tipo_pedido": requisicao.tipo_pedido,
            "objeto": requisicao.objeto,
            "justificativa": requisicao.justificativa,
            "valor_estimado": requisicao.valor_estimado,
            "prazo_necessidade": requisicao.prazo_necessidade.isoformat() if requisicao.prazo_necessidade else None,
            "local_execucao": requisicao.local_execucao,
            "especificacoes_tecnicas": requisicao.especificacoes_tecnicas,
            "quantidade": requisicao.quantidade,
            "unidade_medida": requisicao.unidade_medida,
            "criterios_selecao": requisicao.criterios_selecao,
            "observacoes": requisicao.observacoes,
            "prioridade": requisicao.prioridade,
            "categoria": requisicao.categoria
        },
        "status": {
            "atual": requisicao.status,
            "data_criacao": requisicao.data_criacao.isoformat(),
            "data_atualizacao": requisicao.data_atualizacao.isoformat(),
            "etapa_atual": workflow_status.etapa_atual if workflow_status else "criada",
            "status_etapa": workflow_status.status_etapa if workflow_status else "pendente"
        },
        "aprovacoes": [
            {
                "nivel": aprov.nivel_aprovacao,
                "aprovador": aprov.aprovador_nome,
                "decisao": aprov.decisao,
                "data_decisao": aprov.data_decisao.isoformat(),
                "comentarios": aprov.comentarios
            }
            for aprov in aprovacoes
        ],
        "analise_ambiental": {
            "impacto": analise_ambiental.impacto_ambiental,
            "analise_detalhada": analise_ambiental.analise_detalhada,
            "recomendacoes": analise_ambiental.recomendacoes
        } if analise_ambiental else None
    }

@router.put("/{requisicao_id}/aprovar")
def aprovar_requisicao(
    requisicao_id: str,
    aprovacao: AprovacaoRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Aprova ou rejeita uma requisição.
    
    Args:
        requisicao_id: ID da requisição
        aprovacao: Dados da aprovação
        background_tasks: Para processamento em background
        db: Sessão do banco de dados
    
    Returns:
        dict: Confirmação da aprovação
    """
    requisicao = db.query(RequisicaoInterna).filter(RequisicaoInterna.id == requisicao_id).first()
    
    if not requisicao:
        raise HTTPException(status_code=404, detail="Requisição não encontrada")
    
    # Determinar o nível de aprovação baseado no status atual
    nivel_aprovacao = determinar_nivel_aprovacao(requisicao.status)
    ordem_aprovacao = obter_ordem_aprovacao(nivel_aprovacao)
    
    # Criar registro de aprovação
    aprovacao_registro = AprovacaoRequisicao(
        id=str(uuid.uuid4()),
        requisicao_id=requisicao_id,
        aprovador_nome=aprovacao.aprovador_nome,
        aprovador_email=aprovacao.aprovador_email,
        aprovador_cargo=aprovacao.aprovador_cargo,
        nivel_aprovacao=nivel_aprovacao,
        decisao=aprovacao.decisao,
        comentarios=aprovacao.comentarios,
        ordem_aprovacao=ordem_aprovacao,
        status="processado"
    )
    
    db.add(aprovacao_registro)
    
    # Atualizar status da requisição
    if aprovacao.decisao == "aprovado":
        novo_status = obter_proximo_status(requisicao.status)
        requisicao.status = novo_status
        
        # Se chegou na análise da IA, iniciar processo
        if novo_status == "analise_ia":
            background_tasks.add_task(
                iniciar_analise_ia,
                requisicao_id
            )
    else:
        requisicao.status = "rejeitado"
    
    requisicao.data_atualizacao = datetime.now()
    
    # Atualizar workflow status
    workflow_status = WorkflowStatus(
        id=str(uuid.uuid4()),
        requisicao_id=requisicao_id,
        etapa_atual=requisicao.status,
        status_etapa="concluida" if aprovacao.decisao == "aprovado" else "rejeitada",
        data_conclusao=datetime.now(),
        responsavel_atual=aprovacao.aprovador_nome
    )
    
    db.add(workflow_status)
    db.commit()
    
    return {
        "sucesso": True,
        "requisicao_id": requisicao_id,
        "decisao": aprovacao.decisao,
        "novo_status": requisicao.status,
        "nivel_aprovacao": nivel_aprovacao,
        "data_aprovacao": datetime.now().isoformat()
    }

@router.get("/{requisicao_id}/workflow")
def obter_workflow_status(requisicao_id: str, db: Session = Depends(get_db)):
    """
    Obtém o status atual do workflow de uma requisição.
    
    Args:
        requisicao_id: ID da requisição
        db: Sessão do banco de dados
    
    Returns:
        dict: Status do workflow
    """
    requisicao = db.query(RequisicaoInterna).filter(RequisicaoInterna.id == requisicao_id).first()
    
    if not requisicao:
        raise HTTPException(status_code=404, detail="Requisição não encontrada")
    
    # Buscar todos os status do workflow
    workflow_steps = db.query(WorkflowStatus).filter(
        WorkflowStatus.requisicao_id == requisicao_id
    ).order_by(WorkflowStatus.data_inicio).all()
    
    # Buscar aprovações
    aprovacoes = db.query(AprovacaoRequisicao).filter(
        AprovacaoRequisicao.requisicao_id == requisicao_id
    ).order_by(AprovacaoRequisicao.ordem_aprovacao).all()
    
    return {
        "requisicao_id": requisicao_id,
        "numero_requisicao": requisicao.numero_requisicao,
        "status_atual": requisicao.status,
        "etapas_workflow": [
            {
                "etapa": step.etapa_atual,
                "status": step.status_etapa,
                "data_inicio": step.data_inicio.isoformat(),
                "data_conclusao": step.data_conclusao.isoformat() if step.data_conclusao else None,
                "responsavel": step.responsavel_atual,
                "observacoes": step.observacoes
            }
            for step in workflow_steps
        ],
        "aprovacoes": [
            {
                "nivel": aprov.nivel_aprovacao,
                "aprovador": aprov.aprovador_nome,
                "decisao": aprov.decisao,
                "data_decisao": aprov.data_decisao.isoformat(),
                "comentarios": aprov.comentarios
            }
            for aprov in aprovacoes
        ],
        "proxima_etapa": obter_proxima_etapa(requisicao.status)
    }

@router.get("/dashboard/gerencial")
def dashboard_gerencial(
    periodo_dias: int = 30,
    db: Session = Depends(get_db)
):
    """
    Dashboard gerencial com métricas das requisições.
    
    Args:
        periodo_dias: Período em dias para análise
        db: Sessão do banco de dados
    
    Returns:
        dict: Dashboard com métricas
    """
    from datetime import timedelta
    
    data_inicio = datetime.now() - timedelta(days=periodo_dias)
    
    # Consultas básicas
    total_requisicoes = db.query(RequisicaoInterna).filter(
        RequisicaoInterna.data_criacao >= data_inicio
    ).count()
    
    # Distribuição por status
    status_counts = db.query(
        RequisicaoInterna.status,
        db.func.count(RequisicaoInterna.id)
    ).filter(
        RequisicaoInterna.data_criacao >= data_inicio
    ).group_by(RequisicaoInterna.status).all()
    
    # Distribuição por setor
    setor_counts = db.query(
        RequisicaoInterna.setor_solicitante,
        db.func.count(RequisicaoInterna.id)
    ).filter(
        RequisicaoInterna.data_criacao >= data_inicio
    ).group_by(RequisicaoInterna.setor_solicitante).all()
    
    # Distribuição por prioridade
    prioridade_counts = db.query(
        RequisicaoInterna.prioridade,
        db.func.count(RequisicaoInterna.id)
    ).filter(
        RequisicaoInterna.data_criacao >= data_inicio
    ).group_by(RequisicaoInterna.prioridade).all()
    
    # Valor total das requisições
    valor_total = db.query(
        db.func.sum(RequisicaoInterna.valor_estimado)
    ).filter(
        RequisicaoInterna.data_criacao >= data_inicio,
        RequisicaoInterna.valor_estimado.isnot(None)
    ).scalar() or 0
    
    return {
        "periodo_analise": f"{periodo_dias} dias",
        "data_inicio": data_inicio.isoformat(),
        "data_fim": datetime.now().isoformat(),
        "metricas_gerais": {
            "total_requisicoes": total_requisicoes,
            "valor_total_estimado": valor_total,
            "media_valor_requisicao": valor_total / total_requisicoes if total_requisicoes > 0 else 0
        },
        "distribuicoes": {
            "por_status": {status: count for status, count in status_counts},
            "por_setor": {setor: count for setor, count in setor_counts},
            "por_prioridade": {prioridade: count for prioridade, count in prioridade_counts}
        },
        "data_atualizacao": datetime.now().isoformat()
    }

# Funções auxiliares

def determinar_nivel_aprovacao(status_atual: str) -> str:
    """Determina o nível de aprovação baseado no status atual."""
    mapping = {
        "pendente": "supervisor",
        "supervisor_aprovado": "compras",
        "compras_aprovado": "orcamento",
        "orcamento_aprovado": "final"
    }
    return mapping.get(status_atual, "supervisor")

def obter_ordem_aprovacao(nivel: str) -> int:
    """Obtém a ordem de aprovação baseada no nível."""
    mapping = {
        "supervisor": 1,
        "compras": 2,
        "orcamento": 3,
        "final": 4
    }
    return mapping.get(nivel, 1)

def obter_proximo_status(status_atual: str) -> str:
    """Obtém o próximo status no workflow."""
    mapping = {
        "pendente": "supervisor_aprovado",
        "supervisor_aprovado": "compras_aprovado",
        "compras_aprovado": "orcamento_aprovado",
        "orcamento_aprovado": "analise_ia",
        "analise_ia": "finalizado"
    }
    return mapping.get(status_atual, "finalizado")

def obter_proxima_etapa(status_atual: str) -> str:
    """Obtém a próxima etapa no workflow."""
    mapping = {
        "pendente": "Aprovação do Supervisor",
        "supervisor_aprovado": "Análise do Setor de Compras",
        "compras_aprovado": "Validação Orçamentária",
        "orcamento_aprovado": "Análise por Agentes IA",
        "analise_ia": "Finalização",
        "finalizado": "Processo Concluído"
    }
    return mapping.get(status_atual, "Processo Concluído")

async def iniciar_workflow_aprovacao(requisicao_id: str):
    """Inicia o workflow de aprovação em background."""
    print(f"Iniciando workflow de aprovação para requisição {requisicao_id}")
    # Aqui seria implementada a lógica de notificação dos aprovadores
    # Por exemplo: envio de e-mail, notificação no sistema, etc.

async def iniciar_analise_ia(requisicao_id: str):
    """Inicia a análise por agentes IA em background."""
    print(f"Iniciando análise por agentes IA para requisição {requisicao_id}")
    # Aqui seria chamado o sistema de agentes IA
    # resultado = run_requisicao_analysis_crew(requisicao_id)