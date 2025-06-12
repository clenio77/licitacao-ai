"""
Endpoints da API para geração de editais de licitação.
Fornece interface REST para o sistema de geração automatizada.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json
import uuid

from api.database import get_db, EditalRequest, EditalGerado, HistoricoEdital, TemplateEdital
from api.edital_models import (
    EditalRequest as EditalRequestModel,
    EditalResponse,
    HistoricoEdital as HistoricoEditalModel,
    TemplateEdital as TemplateEditalModel,
    StatusEdital,
    NivelRisco
)
from crewai_agents.edital_main import run_edital_generation_crew

# Router para endpoints de edital
router = APIRouter(prefix="/api/editais", tags=["Geração de Editais"])

@router.post("/gerar", response_model=dict)
async def gerar_edital(
    request: EditalRequestModel,
    background_tasks: BackgroundTasks,
    user_id: str = "sistema",
    db: Session = Depends(get_db)
):
    """
    Inicia o processo de geração de edital baseado nos requisitos fornecidos.
    
    Args:
        request: Dados da solicitação de edital
        background_tasks: Para processamento em background
        user_id: ID do usuário solicitante
        db: Sessão do banco de dados
    
    Returns:
        dict: Informações sobre o processo iniciado
    """
    try:
        # Converter request para dict
        request_data = request.dict()
        
        # Gerar ID único para a solicitação
        request_id = str(uuid.uuid4())
        
        # Salvar solicitação inicial no banco
        edital_request = EditalRequest(
            id=request_id,
            objeto=request_data['objeto'],
            tipo_licitacao=request_data['tipo_licitacao'],
            modalidade=request_data['modalidade'],
            categoria=request_data['categoria'],
            setor_requisitante=request_data['setor_requisitante'],
            itens=request_data['itens'],
            requisitos_tecnicos=request_data.get('requisitos_tecnicos', []),
            requisitos_juridicos=request_data.get('requisitos_juridicos', []),
            valor_total_estimado=request_data.get('valor_total_estimado'),
            prazo_execucao=request_data.get('prazo_execucao'),
            prazo_proposta=request_data.get('prazo_proposta', 7),
            permite_consorcio=request_data.get('permite_consorcio', False),
            exige_visita_tecnica=request_data.get('exige_visita_tecnica', False),
            criterio_julgamento=request_data.get('criterio_julgamento', 'menor_preco'),
            observacoes=request_data.get('observacoes'),
            referencias_editais=request_data.get('referencias_editais'),
            criado_por=user_id,
            status="processando"
        )
        
        db.add(edital_request)
        db.commit()
        
        # Iniciar processamento em background
        background_tasks.add_task(
            processar_geracao_edital,
            request_data,
            request_id,
            user_id
        )
        
        return {
            "sucesso": True,
            "request_id": request_id,
            "status": "processando",
            "mensagem": "Processo de geração iniciado. Use o request_id para acompanhar o progresso.",
            "data_inicio": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao iniciar geração: {str(e)}")

async def processar_geracao_edital(request_data: dict, request_id: str, user_id: str):
    """
    Função para processar a geração do edital em background.
    
    Args:
        request_data: Dados da solicitação
        request_id: ID da solicitação
        user_id: ID do usuário
    """
    try:
        # Executar o processo de geração
        resultado = run_edital_generation_crew(request_data, user_id)
        
        # Atualizar status no banco
        db = next(get_db())
        edital_request = db.query(EditalRequest).filter(EditalRequest.id == request_id).first()
        
        if edital_request:
            if resultado.get('sucesso'):
                edital_request.status = "concluido"
            else:
                edital_request.status = "erro"
            
            db.commit()
        
        db.close()
        
    except Exception as e:
        # Atualizar status para erro
        db = next(get_db())
        edital_request = db.query(EditalRequest).filter(EditalRequest.id == request_id).first()
        
        if edital_request:
            edital_request.status = "erro"
            db.commit()
        
        db.close()
        print(f"Erro no processamento: {str(e)}")

@router.get("/status/{request_id}")
def verificar_status(request_id: str, db: Session = Depends(get_db)):
    """
    Verifica o status de uma solicitação de geração de edital.
    
    Args:
        request_id: ID da solicitação
        db: Sessão do banco de dados
    
    Returns:
        dict: Status atual da solicitação
    """
    edital_request = db.query(EditalRequest).filter(EditalRequest.id == request_id).first()
    
    if not edital_request:
        raise HTTPException(status_code=404, detail="Solicitação não encontrada")
    
    # Buscar edital gerado se existir
    edital_gerado = None
    if edital_request.status == "concluido":
        edital_gerado = db.query(EditalGerado).filter(EditalGerado.request_id == request_id).first()
    
    return {
        "request_id": request_id,
        "status": edital_request.status,
        "objeto": edital_request.objeto,
        "data_criacao": edital_request.data_criacao.isoformat(),
        "edital_id": edital_gerado.id if edital_gerado else None,
        "edital_disponivel": edital_gerado is not None
    }

@router.get("/", response_model=List[dict])
def listar_editais_gerados(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Lista editais gerados com filtros opcionais.
    
    Args:
        skip: Registros a pular (paginação)
        limit: Limite de registros
        status: Filtro por status
        db: Sessão do banco de dados
    
    Returns:
        List[dict]: Lista de editais gerados
    """
    query = db.query(EditalGerado)
    
    if status:
        query = query.filter(EditalGerado.status == status)
    
    editais = query.offset(skip).limit(limit).all()
    
    resultado = []
    for edital in editais:
        # Buscar dados da solicitação original
        request_data = db.query(EditalRequest).filter(EditalRequest.id == edital.request_id).first()
        
        resultado.append({
            "id": edital.id,
            "numero_edital": edital.numero_edital,
            "objeto": request_data.objeto if request_data else "N/A",
            "status": edital.status,
            "data_criacao": edital.data_criacao.isoformat(),
            "criado_por": edital.criado_por,
            "versao": edital.versao
        })
    
    return resultado

@router.get("/{edital_id}", response_model=dict)
def obter_edital(edital_id: str, db: Session = Depends(get_db)):
    """
    Obtém um edital específico pelo ID.
    
    Args:
        edital_id: ID do edital
        db: Sessão do banco de dados
    
    Returns:
        dict: Dados completos do edital
    """
    edital = db.query(EditalGerado).filter(EditalGerado.id == edital_id).first()
    
    if not edital:
        raise HTTPException(status_code=404, detail="Edital não encontrado")
    
    # Buscar dados da solicitação original
    request_data = db.query(EditalRequest).filter(EditalRequest.id == edital.request_id).first()
    
    return {
        "id": edital.id,
        "numero_edital": edital.numero_edital,
        "request_id": edital.request_id,
        "conteudo_edital": edital.conteudo_edital,
        "status": edital.status,
        "data_criacao": edital.data_criacao.isoformat(),
        "data_modificacao": edital.data_modificacao.isoformat() if edital.data_modificacao else None,
        "criado_por": edital.criado_por,
        "versao": edital.versao,
        "analise_juridica": edital.analise_juridica,
        "analise_tecnica": edital.analise_tecnica,
        "analise_financeira": edital.analise_financeira,
        "analise_risco": edital.analise_risco,
        "anexos": edital.anexos,
        "editais_referencia": edital.editais_referencia,
        "melhorias_aplicadas": edital.melhorias_aplicadas,
        # Dados da solicitação original
        "solicitacao_original": {
            "objeto": request_data.objeto,
            "tipo_licitacao": request_data.tipo_licitacao,
            "categoria": request_data.categoria,
            "setor_requisitante": request_data.setor_requisitante,
            "valor_total_estimado": request_data.valor_total_estimado
        } if request_data else None
    }

@router.put("/{edital_id}/status")
def atualizar_status_edital(
    edital_id: str,
    novo_status: StatusEdital,
    observacoes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Atualiza o status de um edital.
    
    Args:
        edital_id: ID do edital
        novo_status: Novo status
        observacoes: Observações sobre a mudança
        db: Sessão do banco de dados
    
    Returns:
        dict: Confirmação da atualização
    """
    edital = db.query(EditalGerado).filter(EditalGerado.id == edital_id).first()
    
    if not edital:
        raise HTTPException(status_code=404, detail="Edital não encontrado")
    
    status_anterior = edital.status
    edital.status = novo_status.value
    edital.data_modificacao = datetime.now()
    
    db.commit()
    
    return {
        "sucesso": True,
        "edital_id": edital_id,
        "status_anterior": status_anterior,
        "status_atual": novo_status.value,
        "data_atualizacao": datetime.now().isoformat(),
        "observacoes": observacoes
    }

@router.get("/templates/", response_model=List[dict])
def listar_templates(
    categoria: Optional[str] = None,
    tipo_licitacao: Optional[str] = None,
    ativo: bool = True,
    db: Session = Depends(get_db)
):
    """
    Lista templates de editais disponíveis.
    
    Args:
        categoria: Filtro por categoria
        tipo_licitacao: Filtro por tipo de licitação
        ativo: Filtro por templates ativos
        db: Sessão do banco de dados
    
    Returns:
        List[dict]: Lista de templates
    """
    query = db.query(TemplateEdital)
    
    if categoria:
        query = query.filter(TemplateEdital.categoria == categoria)
    
    if tipo_licitacao:
        query = query.filter(TemplateEdital.tipo_licitacao == tipo_licitacao)
    
    if ativo is not None:
        query = query.filter(TemplateEdital.ativo == ativo)
    
    templates = query.all()
    
    return [
        {
            "id": t.id,
            "nome": t.nome,
            "categoria": t.categoria,
            "tipo_licitacao": t.tipo_licitacao,
            "versao": t.versao,
            "ativo": t.ativo,
            "vezes_usado": t.vezes_usado,
            "taxa_sucesso": t.taxa_sucesso,
            "data_criacao": t.data_criacao.isoformat()
        }
        for t in templates
    ]

@router.post("/historico/")
def registrar_resultado_edital(
    edital_id: str,
    sucesso: bool,
    motivo_fracasso: Optional[str] = None,
    licoes_aprendidas: Optional[List[str]] = None,
    numero_propostas: Optional[int] = None,
    valor_contratado: Optional[float] = None,
    user_id: str = "sistema",
    db: Session = Depends(get_db)
):
    """
    Registra o resultado de um edital para aprendizado do sistema.
    
    Args:
        edital_id: ID do edital
        sucesso: Se foi bem-sucedido
        motivo_fracasso: Motivo do fracasso se aplicável
        licoes_aprendidas: Lições aprendidas
        numero_propostas: Número de propostas recebidas
        valor_contratado: Valor final contratado
        user_id: ID do usuário
        db: Sessão do banco de dados
    
    Returns:
        dict: Confirmação do registro
    """
    # Buscar edital
    edital = db.query(EditalGerado).filter(EditalGerado.id == edital_id).first()
    
    if not edital:
        raise HTTPException(status_code=404, detail="Edital não encontrado")
    
    # Buscar dados da solicitação
    request_data = db.query(EditalRequest).filter(EditalRequest.id == edital.request_id).first()
    
    # Criar registro no histórico
    historico = HistoricoEdital(
        id=str(uuid.uuid4()),
        id_edital=edital_id,
        objeto=request_data.objeto if request_data else "N/A",
        categoria=request_data.categoria if request_data else "N/A",
        tipo_licitacao=request_data.tipo_licitacao if request_data else "N/A",
        sucesso=sucesso,
        motivo_fracasso=motivo_fracasso,
        licoes_aprendidas=licoes_aprendidas or [],
        data_resultado=datetime.now(),
        valor_contratado=valor_contratado,
        numero_propostas=numero_propostas,
        criado_por=user_id
    )
    
    db.add(historico)
    db.commit()
    
    return {
        "sucesso": True,
        "historico_id": historico.id,
        "edital_id": edital_id,
        "resultado_registrado": sucesso,
        "data_registro": datetime.now().isoformat()
    }
