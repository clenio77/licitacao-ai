"""
Endpoints da API para gestão de requisições de análise.
Permite criar, consultar e gerenciar requisições de análise de licitações.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json
import uuid

from api.database import get_db
from pydantic import BaseModel

# Router para endpoints de requisições
router = APIRouter(prefix="/api/requisicoes", tags=["Requisições de Análise"])

# Modelos Pydantic para requests
class RequisicoesAnaliseRequest(BaseModel):
    tipo_analise: str  # 'juridica', 'mercado', 'risco', 'cambial', 'completa'
    prioridade: str = "media"  # 'baixa', 'media', 'alta', 'urgente'
    observacoes: Optional[str] = None
    licitacoes_ids: List[str] = []
    setor_solicitante: Optional[str] = None
    usuario_solicitante: Optional[str] = None

class RequisicoesAnaliseResponse(BaseModel):
    id: str
    tipo_analise: str
    prioridade: str
    status: str
    data_criacao: datetime
    data_conclusao: Optional[datetime] = None
    resultados: Optional[dict] = None
    observacoes: Optional[str] = None

# Simulação de banco de dados em memória (em produção usaria banco real)
requisicoes_db = {}

@router.post("/", response_model=RequisicoesAnaliseResponse)
async def criar_requisicao(
    requisicao: RequisicoesAnaliseRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Cria uma nova requisição de análise para licitações.
    
    Args:
        requisicao: Dados da requisição
        background_tasks: Para processamento em background
        db: Sessão do banco de dados
    
    Returns:
        RequisicoesAnaliseResponse: Dados da requisição criada
    """
    try:
        # Gerar ID único
        requisicao_id = str(uuid.uuid4())
        
        # Criar objeto de requisição
        nova_requisicao = {
            "id": requisicao_id,
            "tipo_analise": requisicao.tipo_analise,
            "prioridade": requisicao.prioridade,
            "status": "pendente",
            "data_criacao": datetime.now(),
            "data_conclusao": None,
            "resultados": None,
            "observacoes": requisicao.observacoes,
            "licitacoes_ids": requisicao.licitacoes_ids,
            "setor_solicitante": requisicao.setor_solicitante,
            "usuario_solicitante": requisicao.usuario_solicitante
        }
        
        # Salvar na "base de dados"
        requisicoes_db[requisicao_id] = nova_requisicao
        
        # Iniciar processamento em background
        background_tasks.add_task(
            processar_requisicao_analise,
            requisicao_id,
            requisicao.tipo_analise,
            requisicao.licitacoes_ids
        )
        
        return RequisicoesAnaliseResponse(**nova_requisicao)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar requisição: {str(e)}")

@router.get("/{requisicao_id}", response_model=RequisicoesAnaliseResponse)
def obter_requisicao(requisicao_id: str):
    """
    Obtém uma requisição específica pelo ID.
    
    Args:
        requisicao_id: ID da requisição
    
    Returns:
        RequisicoesAnaliseResponse: Dados da requisição
    """
    if requisicao_id not in requisicoes_db:
        raise HTTPException(status_code=404, detail="Requisição não encontrada")
    
    requisicao = requisicoes_db[requisicao_id]
    return RequisicoesAnaliseResponse(**requisicao)

@router.get("/", response_model=List[RequisicoesAnaliseResponse])
def listar_requisicoes(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    tipo_analise: Optional[str] = None
):
    """
    Lista requisições com filtros opcionais.
    
    Args:
        skip: Registros a pular (paginação)
        limit: Limite de registros
        status: Filtro por status
        tipo_analise: Filtro por tipo de análise
    
    Returns:
        List[RequisicoesAnaliseResponse]: Lista de requisições
    """
    requisicoes = list(requisicoes_db.values())
    
    # Aplicar filtros
    if status:
        requisicoes = [r for r in requisicoes if r["status"] == status]
    
    if tipo_analise:
        requisicoes = [r for r in requisicoes if r["tipo_analise"] == tipo_analise]
    
    # Ordenar por data de criação (mais recente primeiro)
    requisicoes.sort(key=lambda x: x["data_criacao"], reverse=True)
    
    # Aplicar paginação
    requisicoes = requisicoes[skip:skip+limit]
    
    return [RequisicoesAnaliseResponse(**r) for r in requisicoes]

@router.put("/{requisicao_id}/status")
def atualizar_status_requisicao(
    requisicao_id: str,
    novo_status: str,
    observacoes: Optional[str] = None
):
    """
    Atualiza o status de uma requisição.
    
    Args:
        requisicao_id: ID da requisição
        novo_status: Novo status
        observacoes: Observações sobre a mudança
    
    Returns:
        dict: Confirmação da atualização
    """
    if requisicao_id not in requisicoes_db:
        raise HTTPException(status_code=404, detail="Requisição não encontrada")
    
    requisicao = requisicoes_db[requisicao_id]
    status_anterior = requisicao["status"]
    
    # Atualizar status
    requisicao["status"] = novo_status
    
    # Se concluída, definir data de conclusão
    if novo_status == "concluida":
        requisicao["data_conclusao"] = datetime.now()
    
    # Atualizar observações se fornecidas
    if observacoes:
        requisicao["observacoes"] = observacoes
    
    return {
        "sucesso": True,
        "requisicao_id": requisicao_id,
        "status_anterior": status_anterior,
        "status_atual": novo_status,
        "data_atualizacao": datetime.now().isoformat()
    }

@router.delete("/{requisicao_id}")
def cancelar_requisicao(requisicao_id: str):
    """
    Cancela uma requisição de análise.
    
    Args:
        requisicao_id: ID da requisição
    
    Returns:
        dict: Confirmação do cancelamento
    """
    if requisicao_id not in requisicoes_db:
        raise HTTPException(status_code=404, detail="Requisição não encontrada")
    
    requisicao = requisicoes_db[requisicao_id]
    
    # Verificar se pode ser cancelada
    if requisicao["status"] in ["concluida", "cancelada"]:
        raise HTTPException(
            status_code=400, 
            detail="Requisição já foi concluída ou cancelada"
        )
    
    # Cancelar requisição
    requisicao["status"] = "cancelada"
    requisicao["data_conclusao"] = datetime.now()
    
    return {
        "sucesso": True,
        "requisicao_id": requisicao_id,
        "status": "cancelada",
        "data_cancelamento": datetime.now().isoformat()
    }

# Função para processar requisição em background
async def processar_requisicao_analise(
    requisicao_id: str,
    tipo_analise: str,
    licitacoes_ids: List[str]
):
    """
    Processa uma requisição de análise em background.
    
    Args:
        requisicao_id: ID da requisição
        tipo_analise: Tipo de análise solicitada
        licitacoes_ids: IDs das licitações para análise
    """
    try:
        print(f"🔄 Processando requisição {requisicao_id} - Tipo: {tipo_analise}")
        
        # Simular processamento
        import asyncio
        await asyncio.sleep(2)  # Simular tempo de processamento
        
        # Atualizar status para processando
        if requisicao_id in requisicoes_db:
            requisicoes_db[requisicao_id]["status"] = "processando"
        
        # Simular mais processamento
        await asyncio.sleep(3)
        
        # Simular resultados
        resultados = {
            "tipo_analise": tipo_analise,
            "licitacoes_analisadas": len(licitacoes_ids),
            "resumo": f"Análise {tipo_analise} concluída para {len(licitacoes_ids)} licitações",
            "data_processamento": datetime.now().isoformat()
        }
        
        # Atualizar requisição com resultados
        if requisicao_id in requisicoes_db:
            requisicoes_db[requisicao_id]["status"] = "concluida"
            requisicoes_db[requisicao_id]["resultados"] = resultados
            requisicoes_db[requisicao_id]["data_conclusao"] = datetime.now()
        
        print(f"✅ Requisição {requisicao_id} processada com sucesso")
        
    except Exception as e:
        print(f"❌ Erro ao processar requisição {requisicao_id}: {str(e)}")
        
        # Atualizar status para erro
        if requisicao_id in requisicoes_db:
            requisicoes_db[requisicao_id]["status"] = "erro"
            requisicoes_db[requisicao_id]["data_conclusao"] = datetime.now()
            requisicoes_db[requisicao_id]["observacoes"] = f"Erro no processamento: {str(e)}"