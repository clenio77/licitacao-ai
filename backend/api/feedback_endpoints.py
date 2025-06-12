"""
Endpoints da API para sistema de feedback e melhoria contínua.
Coleta e analisa feedback de todos os stakeholders.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr
import json
import uuid

from api.database import get_db
from api.database_feedback import (
    FeedbackSetor, FeedbackEmpresa, FeedbackLicitacao, 
    SessaoFeedback, AnaliseImpacto, ConfiguracaoFeedback
)

# Router para endpoints de feedback
router = APIRouter(prefix="/api/feedback", tags=["Sistema de Feedback"])

# Modelos Pydantic para requests
class FeedbackSetorRequest(BaseModel):
    edital_id: str
    setor_nome: str
    responsavel_nome: str
    responsavel_email: EmailStr
    responsavel_cargo: Optional[str] = None
    
    # Avaliações (1-5)
    facilidade_uso: int
    qualidade_edital: int
    adequacao_requisitos: int
    tempo_processamento: int
    clareza_especificacoes: int
    
    # Feedback qualitativo
    pontos_positivos: Optional[str] = None
    pontos_negativos: Optional[str] = None
    sugestoes_melhoria: Optional[str] = None
    problemas_encontrados: Optional[str] = None
    
    # Comparação
    preferencia_sistema: bool
    economia_tempo_estimada: Optional[int] = None
    
    # Listas
    areas_melhorar: Optional[List[str]] = []
    funcionalidades_desejadas: Optional[List[str]] = []

class FeedbackEmpresaRequest(BaseModel):
    edital_id: str
    empresa_cnpj: str
    empresa_nome: str
    empresa_porte: Optional[str] = None
    empresa_segmento: Optional[str] = None
    respondente_nome: Optional[str] = None
    respondente_cargo: Optional[str] = None
    respondente_email: Optional[EmailStr] = None
    
    participou_licitacao: bool
    motivo_nao_participacao: Optional[str] = None
    
    # Avaliações (1-5)
    clareza_objeto: Optional[int] = None
    adequacao_especificacoes: Optional[int] = None
    prazo_elaboracao_proposta: Optional[int] = None
    criterios_julgamento: Optional[int] = None
    exigencias_habilitacao: Optional[int] = None
    valor_estimado: Optional[int] = None
    
    nivel_competitividade: Optional[int] = None
    barreiras_participacao: Optional[List[str]] = []
    
    # Feedback qualitativo
    aspectos_positivos: Optional[str] = None
    aspectos_negativos: Optional[str] = None
    sugestoes_especificas: Optional[str] = None
    comparacao_outros_editais: Optional[str] = None
    
    interesse_futuras_licitacoes: Optional[bool] = None
    recomendaria_outros_fornecedores: Optional[bool] = None

class FeedbackLicitacaoRequest(BaseModel):
    edital_id: str
    avaliador_nome: str
    avaliador_cargo: str
    avaliador_experiencia: Optional[int] = None
    
    # Avaliações (1-5)
    qualidade_tecnica: int
    conformidade_legal: int
    adequacao_modalidade: int
    clareza_redacao: int
    completude_documentos: int
    
    # Resultados
    numero_propostas_recebidas: Optional[int] = None
    numero_empresas_habilitadas: Optional[int] = None
    houve_impugnacoes: bool = False
    numero_impugnacoes: Optional[int] = 0
    principais_questionamentos: Optional[List[str]] = []
    
    tempo_analise_propostas: Optional[float] = None
    complexidade_julgamento: Optional[int] = None
    necessidade_esclarecimentos: bool = False
    
    # Comparações
    qualidade_vs_manual: Optional[int] = None
    tempo_vs_manual: Optional[int] = None
    
    # Feedback qualitativo
    pontos_fortes: Optional[str] = None
    areas_melhoria: Optional[str] = None
    erros_identificados: Optional[str] = None
    sugestoes_tecnicas: Optional[str] = None
    
    # Impactos
    reducao_retrabalho: bool = False
    melhoria_padronizacao: bool = False
    facilidade_acompanhamento: bool = False
    
    fase_licitacao: str = "julgamento"

@router.post("/setor")
def registrar_feedback_setor(
    feedback: FeedbackSetorRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Registra feedback do setor requisitante sobre o edital gerado.
    """
    try:
        # Criar registro de feedback
        feedback_db = FeedbackSetor(
            edital_id=feedback.edital_id,
            setor_nome=feedback.setor_nome,
            responsavel_nome=feedback.responsavel_nome,
            responsavel_email=feedback.responsavel_email,
            responsavel_cargo=feedback.responsavel_cargo,
            facilidade_uso=feedback.facilidade_uso,
            qualidade_edital=feedback.qualidade_edital,
            adequacao_requisitos=feedback.adequacao_requisitos,
            tempo_processamento=feedback.tempo_processamento,
            clareza_especificacoes=feedback.clareza_especificacoes,
            pontos_positivos=feedback.pontos_positivos,
            pontos_negativos=feedback.pontos_negativos,
            sugestoes_melhoria=feedback.sugestoes_melhoria,
            problemas_encontrados=feedback.problemas_encontrados,
            preferencia_sistema=feedback.preferencia_sistema,
            economia_tempo_estimada=feedback.economia_tempo_estimada,
            areas_melhorar=feedback.areas_melhorar,
            funcionalidades_desejadas=feedback.funcionalidades_desejadas
        )
        
        db.add(feedback_db)
        db.commit()
        
        # Processar feedback em background
        background_tasks.add_task(processar_feedback_setor, feedback_db.id)
        
        return {
            "sucesso": True,
            "feedback_id": feedback_db.id,
            "mensagem": "Feedback registrado com sucesso. Obrigado pela contribuição!",
            "data_registro": datetime.now().isoformat()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao registrar feedback: {str(e)}")

@router.post("/empresa")
def registrar_feedback_empresa(
    feedback: FeedbackEmpresaRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Registra feedback de empresa licitante sobre o edital.
    """
    try:
        feedback_db = FeedbackEmpresa(
            edital_id=feedback.edital_id,
            empresa_cnpj=feedback.empresa_cnpj,
            empresa_nome=feedback.empresa_nome,
            empresa_porte=feedback.empresa_porte,
            empresa_segmento=feedback.empresa_segmento,
            respondente_nome=feedback.respondente_nome,
            respondente_cargo=feedback.respondente_cargo,
            respondente_email=feedback.respondente_email,
            participou_licitacao=feedback.participou_licitacao,
            motivo_nao_participacao=feedback.motivo_nao_participacao,
            clareza_objeto=feedback.clareza_objeto,
            adequacao_especificacoes=feedback.adequacao_especificacoes,
            prazo_elaboracao_proposta=feedback.prazo_elaboracao_proposta,
            criterios_julgamento=feedback.criterios_julgamento,
            exigencias_habilitacao=feedback.exigencias_habilitacao,
            valor_estimado=feedback.valor_estimado,
            nivel_competitividade=feedback.nivel_competitividade,
            barreiras_participacao=feedback.barreiras_participacao,
            aspectos_positivos=feedback.aspectos_positivos,
            aspectos_negativos=feedback.aspectos_negativos,
            sugestoes_especificas=feedback.sugestoes_especificas,
            comparacao_outros_editais=feedback.comparacao_outros_editais,
            interesse_futuras_licitacoes=feedback.interesse_futuras_licitacoes,
            recomendaria_outros_fornecedores=feedback.recomendaria_outros_fornecedores,
            forma_coleta="formulario_web"
        )
        
        db.add(feedback_db)
        db.commit()
        
        # Processar feedback em background
        background_tasks.add_task(processar_feedback_empresa, feedback_db.id)
        
        return {
            "sucesso": True,
            "feedback_id": feedback_db.id,
            "mensagem": "Feedback registrado com sucesso. Sua opinião é muito importante!",
            "data_registro": datetime.now().isoformat()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao registrar feedback: {str(e)}")

@router.post("/licitacao")
def registrar_feedback_licitacao(
    feedback: FeedbackLicitacaoRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Registra feedback do setor de licitação sobre o processo.
    """
    try:
        feedback_db = FeedbackLicitacao(
            edital_id=feedback.edital_id,
            avaliador_nome=feedback.avaliador_nome,
            avaliador_cargo=feedback.avaliador_cargo,
            avaliador_experiencia=feedback.avaliador_experiencia,
            qualidade_tecnica=feedback.qualidade_tecnica,
            conformidade_legal=feedback.conformidade_legal,
            adequacao_modalidade=feedback.adequacao_modalidade,
            clareza_redacao=feedback.clareza_redacao,
            completude_documentos=feedback.completude_documentos,
            numero_propostas_recebidas=feedback.numero_propostas_recebidas,
            numero_empresas_habilitadas=feedback.numero_empresas_habilitadas,
            houve_impugnacoes=feedback.houve_impugnacoes,
            numero_impugnacoes=feedback.numero_impugnacoes,
            principais_questionamentos=feedback.principais_questionamentos,
            tempo_analise_propostas=feedback.tempo_analise_propostas,
            complexidade_julgamento=feedback.complexidade_julgamento,
            necessidade_esclarecimentos=feedback.necessidade_esclarecimentos,
            qualidade_vs_manual=feedback.qualidade_vs_manual,
            tempo_vs_manual=feedback.tempo_vs_manual,
            pontos_fortes=feedback.pontos_fortes,
            areas_melhoria=feedback.areas_melhoria,
            erros_identificados=feedback.erros_identificados,
            sugestoes_tecnicas=feedback.sugestoes_tecnicas,
            reducao_retrabalho=feedback.reducao_retrabalho,
            melhoria_padronizacao=feedback.melhoria_padronizacao,
            facilidade_acompanhamento=feedback.facilidade_acompanhamento,
            fase_licitacao=feedback.fase_licitacao
        )
        
        db.add(feedback_db)
        db.commit()
        
        # Processar feedback em background
        background_tasks.add_task(processar_feedback_licitacao, feedback_db.id)
        
        return {
            "sucesso": True,
            "feedback_id": feedback_db.id,
            "mensagem": "Feedback técnico registrado com sucesso!",
            "data_registro": datetime.now().isoformat()
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao registrar feedback: {str(e)}")

@router.get("/analytics/dashboard")
def dashboard_feedback(
    periodo_dias: int = Query(30, description="Período em dias para análise"),
    db: Session = Depends(get_db)
):
    """
    Dashboard com analytics consolidados de feedback.
    """
    try:
        data_inicio = datetime.now() - timedelta(days=periodo_dias)
        
        # Estatísticas gerais
        total_feedbacks_setor = db.query(FeedbackSetor).filter(
            FeedbackSetor.data_feedback >= data_inicio
        ).count()
        
        total_feedbacks_empresa = db.query(FeedbackEmpresa).filter(
            FeedbackEmpresa.data_feedback >= data_inicio
        ).count()
        
        total_feedbacks_licitacao = db.query(FeedbackLicitacao).filter(
            FeedbackLicitacao.data_feedback >= data_inicio
        ).count()
        
        # Médias de satisfação
        feedbacks_setor = db.query(FeedbackSetor).filter(
            FeedbackSetor.data_feedback >= data_inicio
        ).all()
        
        if feedbacks_setor:
            media_satisfacao_setor = sum([
                (f.facilidade_uso + f.qualidade_edital + f.adequacao_requisitos + 
                 f.tempo_processamento + f.clareza_especificacoes) / 5
                for f in feedbacks_setor
            ]) / len(feedbacks_setor)
        else:
            media_satisfacao_setor = 0
        
        # Principais problemas identificados
        problemas_frequentes = {}
        for feedback in feedbacks_setor:
            if feedback.problemas_encontrados:
                problemas_frequentes[feedback.problemas_encontrados] = \
                    problemas_frequentes.get(feedback.problemas_encontrados, 0) + 1
        
        # Sugestões mais comuns
        sugestoes_frequentes = {}
        for feedback in feedbacks_setor:
            if feedback.sugestoes_melhoria:
                sugestoes_frequentes[feedback.sugestoes_melhoria] = \
                    sugestoes_frequentes.get(feedback.sugestoes_melhoria, 0) + 1
        
        return {
            "periodo_analise": f"{periodo_dias} dias",
            "data_inicio": data_inicio.isoformat(),
            "data_fim": datetime.now().isoformat(),
            "estatisticas_gerais": {
                "total_feedbacks_setor": total_feedbacks_setor,
                "total_feedbacks_empresa": total_feedbacks_empresa,
                "total_feedbacks_licitacao": total_feedbacks_licitacao,
                "total_geral": total_feedbacks_setor + total_feedbacks_empresa + total_feedbacks_licitacao
            },
            "satisfacao": {
                "media_setor": round(media_satisfacao_setor, 2),
                "escala": "1-5 (1=Muito Insatisfeito, 5=Muito Satisfeito)"
            },
            "insights": {
                "problemas_mais_frequentes": dict(sorted(problemas_frequentes.items(), 
                                                        key=lambda x: x[1], reverse=True)[:5]),
                "sugestoes_mais_comuns": dict(sorted(sugestoes_frequentes.items(), 
                                                   key=lambda x: x[1], reverse=True)[:5])
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar dashboard: {str(e)}")

@router.get("/relatorio/melhorias")
def relatorio_melhorias_implementadas(
    db: Session = Depends(get_db)
):
    """
    Relatório de melhorias implementadas baseadas em feedback.
    """
    try:
        melhorias = db.query(AnaliseImpacto).order_by(AnaliseImpacto.data_implementacao.desc()).all()
        
        resultado = []
        for melhoria in melhorias:
            resultado.append({
                "id": melhoria.id,
                "titulo": melhoria.titulo_melhoria,
                "categoria": melhoria.categoria_melhoria,
                "data_implementacao": melhoria.data_implementacao.isoformat(),
                "impacto_qualitativo": melhoria.impacto_qualitativo,
                "roi_calculado": melhoria.roi_calculado,
                "satisfacao_geral": {
                    "setores": melhoria.satisfacao_setores,
                    "empresas": melhoria.satisfacao_empresas,
                    "licitacao": melhoria.satisfacao_licitacao
                },
                "status": melhoria.status_implementacao
            })
        
        return {
            "total_melhorias": len(resultado),
            "melhorias": resultado,
            "data_relatorio": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar relatório: {str(e)}")

# Funções de processamento em background
async def processar_feedback_setor(feedback_id: str):
    """Processa feedback do setor em background"""
    # Aqui seria implementada análise automática do feedback
    # Por exemplo: identificar padrões, gerar alertas, etc.
    print(f"Processando feedback do setor: {feedback_id}")

async def processar_feedback_empresa(feedback_id: str):
    """Processa feedback da empresa em background"""
    print(f"Processando feedback da empresa: {feedback_id}")

async def processar_feedback_licitacao(feedback_id: str):
    """Processa feedback do setor de licitação em background"""
    print(f"Processando feedback do setor de licitação: {feedback_id}")

@router.post("/sessao")
def agendar_sessao_feedback(
    titulo: str,
    tipo_sessao: str,
    data_sessao: datetime,
    descricao: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Agenda uma sessão de feedback coletivo (workshop, reunião, etc.).
    """
    try:
        sessao = SessaoFeedback(
            tipo_sessao=tipo_sessao,
            titulo=titulo,
            descricao=descricao,
            data_sessao=data_sessao,
            status="planejada"
        )
        
        db.add(sessao)
        db.commit()
        
        return {
            "sucesso": True,
            "sessao_id": sessao.id,
            "titulo": titulo,
            "data_sessao": data_sessao.isoformat(),
            "status": "agendada"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao agendar sessão: {str(e)}")

@router.get("/formulario/{tipo}")
def obter_formulario_feedback(tipo: str):
    """
    Retorna estrutura do formulário de feedback para diferentes tipos.
    """
    formularios = {
        "setor": {
            "titulo": "Feedback do Setor Requisitante",
            "descricao": "Avalie sua experiência com o sistema de geração de editais",
            "secoes": [
                {
                    "nome": "Identificação",
                    "campos": ["setor_nome", "responsavel_nome", "responsavel_email", "responsavel_cargo"]
                },
                {
                    "nome": "Avaliação do Sistema",
                    "campos": ["facilidade_uso", "qualidade_edital", "adequacao_requisitos", 
                             "tempo_processamento", "clareza_especificacoes"]
                },
                {
                    "nome": "Feedback Qualitativo",
                    "campos": ["pontos_positivos", "pontos_negativos", "sugestoes_melhoria", "problemas_encontrados"]
                },
                {
                    "nome": "Comparação",
                    "campos": ["preferencia_sistema", "economia_tempo_estimada"]
                }
            ]
        },
        "empresa": {
            "titulo": "Feedback da Empresa Licitante",
            "descricao": "Sua opinião sobre a qualidade do edital é muito importante",
            "secoes": [
                {
                    "nome": "Dados da Empresa",
                    "campos": ["empresa_cnpj", "empresa_nome", "empresa_porte", "respondente_nome"]
                },
                {
                    "nome": "Participação na Licitação",
                    "campos": ["participou_licitacao", "motivo_nao_participacao"]
                },
                {
                    "nome": "Avaliação do Edital",
                    "campos": ["clareza_objeto", "adequacao_especificacoes", "prazo_elaboracao_proposta"]
                }
            ]
        },
        "licitacao": {
            "titulo": "Feedback do Setor de Licitação",
            "descricao": "Avaliação técnica do processo e resultados",
            "secoes": [
                {
                    "nome": "Identificação do Avaliador",
                    "campos": ["avaliador_nome", "avaliador_cargo", "avaliador_experiencia"]
                },
                {
                    "nome": "Avaliação Técnica",
                    "campos": ["qualidade_tecnica", "conformidade_legal", "adequacao_modalidade"]
                },
                {
                    "nome": "Resultados da Licitação",
                    "campos": ["numero_propostas_recebidas", "houve_impugnacoes", "tempo_analise_propostas"]
                }
            ]
        }
    }
    
    if tipo not in formularios:
        raise HTTPException(status_code=404, detail="Tipo de formulário não encontrado")
    
    return formularios[tipo]
