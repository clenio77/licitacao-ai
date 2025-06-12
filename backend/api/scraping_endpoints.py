"""
Endpoints da API para web scraping e gestão da base de conhecimento.
Permite executar coleta de dados e consultar insights.
"""

from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import json
import asyncio

from api.database import get_db
from web_scraping.gov_procurement_scraper import GovProcurementScraper
from crewai_agents.knowledge_base_tools import KnowledgeBaseTool, KnowledgeBaseAnalyticsTool

# Router para endpoints de scraping
router = APIRouter(prefix="/api/scraping", tags=["Web Scraping e Base de Conhecimento"])

@router.post("/executar")
async def executar_scraping(
    background_tasks: BackgroundTasks,
    categorias: Optional[List[str]] = None,
    sites: Optional[List[str]] = None,
    salvar_automatico: bool = True
):
    """
    Executa web scraping para coletar dados de licitações bem-sucedidas.
    
    Args:
        categorias: Lista de categorias para buscar
        sites: Lista de sites para consultar (opcional)
        salvar_automatico: Se deve salvar automaticamente na base de conhecimento
    
    Returns:
        dict: Status da execução e informações do processo
    """
    try:
        # Categorias padrão se não especificadas
        if categorias is None:
            categorias = [
                'serviços de limpeza',
                'equipamentos de informática',
                'material de escritório',
                'serviços de segurança',
                'serviços de manutenção'
            ]
        
        # Iniciar scraping em background
        background_tasks.add_task(
            executar_scraping_background,
            categorias,
            sites,
            salvar_automatico
        )
        
        return {
            "sucesso": True,
            "status": "iniciado",
            "categorias": categorias,
            "sites": sites or ["todos"],
            "mensagem": "Scraping iniciado em background. Use /api/scraping/status para acompanhar.",
            "data_inicio": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao iniciar scraping: {str(e)}")

async def executar_scraping_background(
    categorias: List[str],
    sites: Optional[List[str]],
    salvar_automatico: bool
):
    """
    Função para executar scraping em background.
    
    Args:
        categorias: Lista de categorias para buscar
        sites: Lista de sites para consultar
        salvar_automatico: Se deve salvar automaticamente
    """
    try:
        print(f"🚀 Iniciando scraping para categorias: {categorias}")
        
        # Criar instância do scraper
        scraper = GovProcurementScraper()
        
        # Executar scraping
        licitacoes = await scraper.scrape_all_sites(categorias)
        
        if licitacoes and salvar_automatico:
            # Salvar na base de conhecimento
            filepath = await scraper.save_to_knowledge_base(licitacoes)
            print(f"✅ Scraping concluído. {len(licitacoes)} licitações salvas em {filepath}")
        else:
            print(f"⚠️ Scraping concluído mas nenhuma licitação foi encontrada")
            
    except Exception as e:
        print(f"❌ Erro durante scraping em background: {str(e)}")

@router.get("/status")
def verificar_status_scraping():
    """
    Verifica o status atual do scraping.
    Nota: Em produção, isso seria implementado com Redis ou banco de dados.
    """
    # Simulação de status - em produção usaria Redis/DB para tracking
    return {
        "status": "disponivel",
        "ultimo_scraping": "2024-01-15T10:30:00",
        "proxima_execucao": "2024-01-22T10:30:00",
        "total_licitacoes_base": 150,
        "categorias_disponiveis": [
            "servicos",
            "bens", 
            "obras"
        ]
    }

@router.get("/base-conhecimento/consultar")
def consultar_base_conhecimento(
    categoria: str,
    objeto: Optional[str] = None,
    tipo_licitacao: Optional[str] = None
):
    """
    Consulta a base de conhecimento por categoria e objeto.
    
    Args:
        categoria: Categoria da licitação
        objeto: Descrição do objeto (opcional)
        tipo_licitacao: Tipo de licitação (opcional)
    
    Returns:
        dict: Licitações similares e insights
    """
    try:
        # Usar ferramenta de consulta
        kb_tool = KnowledgeBaseTool()
        resultado = kb_tool._run(categoria, objeto or "", tipo_licitacao or "")
        
        # Parsear resultado JSON
        data = json.loads(resultado)
        
        return {
            "sucesso": True,
            "dados": data,
            "data_consulta": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao consultar base: {str(e)}")

@router.get("/base-conhecimento/analytics")
def analytics_base_conhecimento(tipo_analise: str = "geral"):
    """
    Gera análises estatísticas da base de conhecimento.
    
    Args:
        tipo_analise: Tipo de análise (geral, categoria, tendencias)
    
    Returns:
        dict: Relatório de análise
    """
    try:
        # Usar ferramenta de analytics
        analytics_tool = KnowledgeBaseAnalyticsTool()
        resultado = analytics_tool._run(tipo_analise)
        
        # Parsear resultado JSON
        data = json.loads(resultado)
        
        return {
            "sucesso": True,
            "tipo_analise": tipo_analise,
            "dados": data,
            "data_analise": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na análise: {str(e)}")

@router.get("/base-conhecimento/resumo")
def resumo_base_conhecimento():
    """
    Retorna resumo geral da base de conhecimento.
    
    Returns:
        dict: Resumo com estatísticas principais
    """
    try:
        # Carregar dados da base
        kb_tool = KnowledgeBaseTool()
        data = kb_tool._load_knowledge_base()
        
        if not data:
            return {
                "total_licitacoes": 0,
                "categorias": [],
                "ultima_atualizacao": None,
                "status": "vazia"
            }
        
        # Calcular estatísticas básicas
        categorias = {}
        tipos = {}
        sites = {}
        
        for item in data:
            # Contar categorias
            cat = item.get('categoria', 'indefinida')
            categorias[cat] = categorias.get(cat, 0) + 1
            
            # Contar tipos
            tipo = item.get('tipo_licitacao', 'indefinido')
            tipos[tipo] = tipos.get(tipo, 0) + 1
            
            # Contar sites
            site = item.get('site_origem', 'indefinido')
            sites[site] = sites.get(site, 0) + 1
        
        return {
            "total_licitacoes": len(data),
            "distribuicao_categorias": categorias,
            "distribuicao_tipos": tipos,
            "sites_origem": sites,
            "ultima_atualizacao": datetime.now().isoformat(),
            "status": "ativa"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar resumo: {str(e)}")

@router.post("/agendar")
def agendar_scraping_automatico(
    categorias: List[str],
    frequencia: str = "semanal",
    ativo: bool = True
):
    """
    Agenda execução automática de scraping.
    
    Args:
        categorias: Lista de categorias para monitorar
        frequencia: Frequência da execução (diaria, semanal, mensal)
        ativo: Se o agendamento está ativo
    
    Returns:
        dict: Confirmação do agendamento
    """
    try:
        # Em produção, isso seria salvo no banco e executado via Celery/cron
        agendamento = {
            "id": f"scraping_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "categorias": categorias,
            "frequencia": frequencia,
            "ativo": ativo,
            "data_criacao": datetime.now().isoformat(),
            "proxima_execucao": calcular_proxima_execucao(frequencia)
        }
        
        return {
            "sucesso": True,
            "agendamento": agendamento,
            "mensagem": f"Scraping agendado para {len(categorias)} categorias com frequência {frequencia}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao agendar: {str(e)}")

@router.get("/agendamentos")
def listar_agendamentos():
    """
    Lista agendamentos ativos de scraping.
    
    Returns:
        dict: Lista de agendamentos
    """
    # Simulação - em produção viria do banco de dados
    agendamentos_simulados = [
        {
            "id": "scraping_20240115_103000",
            "categorias": ["servicos", "bens"],
            "frequencia": "semanal",
            "ativo": True,
            "ultima_execucao": "2024-01-15T10:30:00",
            "proxima_execucao": "2024-01-22T10:30:00"
        }
    ]
    
    return {
        "agendamentos": agendamentos_simulados,
        "total": len(agendamentos_simulados)
    }

@router.delete("/agendamentos/{agendamento_id}")
def cancelar_agendamento(agendamento_id: str):
    """
    Cancela um agendamento de scraping.
    
    Args:
        agendamento_id: ID do agendamento
    
    Returns:
        dict: Confirmação do cancelamento
    """
    # Em produção, removeria do banco e cancelaria no Celery
    return {
        "sucesso": True,
        "agendamento_id": agendamento_id,
        "status": "cancelado",
        "data_cancelamento": datetime.now().isoformat()
    }

def calcular_proxima_execucao(frequencia: str) -> str:
    """
    Calcula próxima execução baseada na frequência.
    
    Args:
        frequencia: Frequência (diaria, semanal, mensal)
    
    Returns:
        str: Data/hora da próxima execução
    """
    from datetime import timedelta
    
    now = datetime.now()
    
    if frequencia == "diaria":
        proxima = now + timedelta(days=1)
    elif frequencia == "semanal":
        proxima = now + timedelta(weeks=1)
    elif frequencia == "mensal":
        proxima = now + timedelta(days=30)
    else:
        proxima = now + timedelta(weeks=1)  # Padrão semanal
    
    return proxima.isoformat()
