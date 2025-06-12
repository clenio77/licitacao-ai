#!/usr/bin/env python3
"""
Script de demonstração do sistema completo de feedback e melhoria contínua.
Simula todo o ciclo: coleta → análise → insights → melhorias → impacto.
"""

import asyncio
import json
import sys
import os
from datetime import datetime, timedelta
import uuid

# Adicionar o diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.feedback_automation import FeedbackAutomationService
from crewai_agents.feedback_analysis_tools import FeedbackAnalysisTool, FeedbackPredictionTool

async def main():
    """Demonstração completa do sistema de feedback"""
    print("🎯 DEMONSTRAÇÃO DO SISTEMA DE FEEDBACK E MELHORIA CONTÍNUA")
    print("=" * 70)
    
    # Etapa 1: Simulação de dados de feedback
    print("\n📊 ETAPA 1: Simulando coleta de feedback de stakeholders")
    print("-" * 50)
    
    feedback_data = simular_dados_feedback()
    print(f"✅ Simulados {len(feedback_data['feedback_setor'])} feedbacks de setores")
    print(f"✅ Simulados {len(feedback_data['feedback_empresa'])} feedbacks de empresas")
    print(f"✅ Simulados {len(feedback_data['feedback_licitacao'])} feedbacks de licitação")
    
    # Etapa 2: Análise automática com IA
    print("\n🤖 ETAPA 2: Análise automática com IA")
    print("-" * 50)
    
    analysis_tool = FeedbackAnalysisTool()
    insights = await analisar_feedback_com_ia(analysis_tool, feedback_data)
    print("✅ Análise de IA concluída")
    print("✅ Insights gerados automaticamente")
    
    # Etapa 3: Predição de problemas
    print("\n🔮 ETAPA 3: Predição de problemas em novos editais")
    print("-" * 50)
    
    prediction_tool = FeedbackPredictionTool()
    predicoes = await prever_problemas(prediction_tool, feedback_data)
    print("✅ Predições geradas para novos editais")
    
    # Etapa 4: Automação de coleta
    print("\n📧 ETAPA 4: Automação de coleta de feedback")
    print("-" * 50)
    
    automation_service = FeedbackAutomationService()
    await automation_service.processar_feedback_automatico()
    print("✅ Processo de automação executado")
    
    # Etapa 5: Relatório de impacto
    print("\n📈 ETAPA 5: Relatório de impacto e melhorias")
    print("-" * 50)
    
    relatorio_impacto = gerar_relatorio_impacto(insights, predicoes)
    print("✅ Relatório de impacto gerado")
    
    # Etapa 6: Apresentação dos resultados
    print("\n🎉 RESULTADOS DA DEMONSTRAÇÃO")
    print("=" * 70)
    
    apresentar_resultados(insights, predicoes, relatorio_impacto)
    
    print("\n✨ DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO!")
    print("O sistema está pronto para coletar feedback real e melhorar continuamente!")

def simular_dados_feedback():
    """Simula dados realistas de feedback de todos os stakeholders"""
    
    # Feedback dos setores requisitantes
    feedback_setor = [
        {
            "id": str(uuid.uuid4()),
            "edital_id": "ED-2024-001",
            "setor_nome": "Gerência de Facilities",
            "responsavel_nome": "João Silva",
            "responsavel_email": "joao.silva@correios.com.br",
            "facilidade_uso": 4,
            "qualidade_edital": 4,
            "adequacao_requisitos": 5,
            "tempo_processamento": 5,
            "clareza_especificacoes": 3,
            "pontos_positivos": "Sistema muito rápido e intuitivo. Gerou edital completo em minutos.",
            "pontos_negativos": "Algumas especificações técnicas ficaram muito genéricas.",
            "sugestoes_melhoria": "Incluir mais opções de personalização para especificações técnicas.",
            "problemas_encontrados": "Dificuldade para ajustar critérios de sustentabilidade.",
            "preferencia_sistema": True,
            "economia_tempo_estimada": 80
        },
        {
            "id": str(uuid.uuid4()),
            "edital_id": "ED-2024-002",
            "setor_nome": "TI Corporativa",
            "responsavel_nome": "Maria Santos",
            "responsavel_email": "maria.santos@correios.com.br",
            "facilidade_uso": 5,
            "qualidade_edital": 4,
            "adequacao_requisitos": 4,
            "tempo_processamento": 5,
            "clareza_especificacoes": 4,
            "pontos_positivos": "Interface excelente, processo muito claro e organizado.",
            "pontos_negativos": "Poderia ter mais templates específicos para TI.",
            "sugestoes_melhoria": "Criar templates especializados por área técnica.",
            "preferencia_sistema": True,
            "economia_tempo_estimada": 75
        }
    ]
    
    # Feedback das empresas licitantes
    feedback_empresa = [
        {
            "id": str(uuid.uuid4()),
            "edital_id": "ED-2024-001",
            "empresa_cnpj": "12.345.678/0001-90",
            "empresa_nome": "Limpeza Total Ltda",
            "empresa_porte": "media",
            "participou_licitacao": True,
            "clareza_objeto": 4,
            "adequacao_especificacoes": 3,
            "prazo_elaboracao_proposta": 4,
            "criterios_julgamento": 5,
            "exigencias_habilitacao": 4,
            "valor_estimado": 4,
            "nivel_competitividade": 4,
            "aspectos_positivos": "Edital muito claro e bem estruturado. Critérios justos.",
            "aspectos_negativos": "Algumas especificações muito restritivas para produtos de limpeza.",
            "sugestoes_especificas": "Permitir produtos equivalentes com certificação similar.",
            "interesse_futuras_licitacoes": True,
            "recomendaria_outros_fornecedores": True
        },
        {
            "id": str(uuid.uuid4()),
            "edital_id": "ED-2024-002",
            "empresa_cnpj": "98.765.432/0001-10",
            "empresa_nome": "TechSolutions Corp",
            "empresa_porte": "grande",
            "participou_licitacao": False,
            "motivo_nao_participacao": "Especificações muito restritivas, favorecendo marca específica.",
            "clareza_objeto": 4,
            "adequacao_especificacoes": 2,
            "prazo_elaboracao_proposta": 3,
            "criterios_julgamento": 3,
            "aspectos_negativos": "Especificações direcionadas para marca específica.",
            "sugestoes_especificas": "Usar especificações baseadas em performance, não em marca.",
            "interesse_futuras_licitacoes": False
        }
    ]
    
    # Feedback do setor de licitação
    feedback_licitacao = [
        {
            "id": str(uuid.uuid4()),
            "edital_id": "ED-2024-001",
            "avaliador_nome": "Carlos Pregoeiro",
            "avaliador_cargo": "Pregoeiro",
            "avaliador_experiencia": 10,
            "qualidade_tecnica": 4,
            "conformidade_legal": 5,
            "adequacao_modalidade": 5,
            "clareza_redacao": 4,
            "completude_documentos": 4,
            "numero_propostas_recebidas": 8,
            "numero_empresas_habilitadas": 6,
            "houve_impugnacoes": False,
            "tempo_analise_propostas": 4.5,
            "qualidade_vs_manual": 4,
            "tempo_vs_manual": 5,
            "pontos_fortes": "Edital bem estruturado, documentação completa, processo ágil.",
            "areas_melhoria": "Melhorar especificações técnicas para aumentar competitividade.",
            "sugestoes_tecnicas": "Incluir validação automática de conformidade legal.",
            "reducao_retrabalho": True,
            "melhoria_padronizacao": True,
            "facilidade_acompanhamento": True
        }
    ]
    
    return {
        "feedback_setor": feedback_setor,
        "feedback_empresa": feedback_empresa,
        "feedback_licitacao": feedback_licitacao
    }

async def analisar_feedback_com_ia(analysis_tool, feedback_data):
    """Executa análise de IA sobre os dados de feedback"""
    print("🔍 Executando análise de IA...")
    
    # Converter dados para JSON
    feedback_json = json.dumps(feedback_data, ensure_ascii=False)
    
    # Executar análise completa
    resultado = analysis_tool._run(feedback_json, "completa")
    insights = json.loads(resultado)
    
    print("📊 Principais insights identificados:")
    
    # Mostrar satisfação geral
    if "analise_satisfacao" in insights:
        satisfacao = insights["analise_satisfacao"]
        if "geral" in satisfacao:
            print(f"   • Satisfação geral: {satisfacao['geral'].get('media', 'N/A')}/5")
            print(f"   • Nível: {satisfacao['geral'].get('nivel', 'N/A')}")
    
    # Mostrar problemas identificados
    if "problemas_identificados" in insights:
        problemas = insights["problemas_identificados"]
        if "problemas_criticos" in problemas:
            print(f"   • Problemas críticos: {len(problemas['problemas_criticos'])}")
    
    # Mostrar sugestões priorizadas
    if "sugestoes_priorizadas" in insights:
        sugestoes = insights["sugestoes_priorizadas"]
        if "sugestoes_impacto_alto" in sugestoes:
            print(f"   • Sugestões de alto impacto: {len(sugestoes['sugestoes_impacto_alto'])}")
    
    return insights

async def prever_problemas(prediction_tool, feedback_data):
    """Executa predição de problemas para novos editais"""
    print("🔮 Executando predição de problemas...")
    
    # Simular dados de um novo edital
    novo_edital = {
        "categoria": "servicos",
        "objeto": "Serviços de segurança patrimonial",
        "valor_total_estimado": 150000,
        "tipo_licitacao": "pregao",
        "modalidade": "eletronica",
        "itens": [
            {"descricao": "Vigilância 24h", "quantidade": 12, "unidade": "meses"}
        ],
        "exige_visita_tecnica": True,
        "criterio_julgamento": "menor_preco"
    }
    
    # Executar predição
    edital_json = json.dumps(novo_edital, ensure_ascii=False)
    historico_json = json.dumps(feedback_data, ensure_ascii=False)
    
    resultado = prediction_tool._run(edital_json, historico_json)
    predicoes = json.loads(resultado)
    
    print("⚠️ Riscos identificados para novo edital:")
    for risco in predicoes.get("riscos_identificados", []):
        print(f"   • {risco.get('descricao', 'N/A')} (Prob: {risco.get('probabilidade', 0):.1%})")
    
    print(f"📈 Probabilidade de sucesso: {predicoes.get('probabilidade_sucesso', 0):.1%}")
    
    return predicoes

def gerar_relatorio_impacto(insights, predicoes):
    """Gera relatório de impacto das melhorias"""
    
    relatorio = {
        "data_relatorio": datetime.now().isoformat(),
        "periodo_analise": "30 dias",
        "melhorias_implementadas": [
            {
                "titulo": "Melhoria nas Especificações Técnicas",
                "categoria": "especificacoes",
                "data_implementacao": (datetime.now() - timedelta(days=15)).isoformat(),
                "origem_feedback": "empresas_licitantes",
                "impacto_medido": {
                    "aumento_participacao": "25%",
                    "reducao_impugnacoes": "40%",
                    "melhoria_satisfacao": "0.8 pontos"
                },
                "roi_estimado": 3.2
            },
            {
                "titulo": "Otimização da Interface de Usuário",
                "categoria": "interface",
                "data_implementacao": (datetime.now() - timedelta(days=10)).isoformat(),
                "origem_feedback": "setores_requisitantes",
                "impacto_medido": {
                    "reducao_tempo_criacao": "30%",
                    "melhoria_usabilidade": "1.2 pontos",
                    "reducao_erros_usuario": "50%"
                },
                "roi_estimado": 4.1
            }
        ],
        "melhorias_planejadas": [
            {
                "titulo": "Templates Especializados por Área",
                "prioridade": "alta",
                "prazo_estimado": "30 dias",
                "impacto_esperado": "alto"
            },
            {
                "titulo": "Validação Automática de Conformidade",
                "prioridade": "media",
                "prazo_estimado": "60 dias",
                "impacto_esperado": "medio"
            }
        ],
        "metricas_gerais": {
            "satisfacao_media_antes": 3.2,
            "satisfacao_media_depois": 4.1,
            "tempo_medio_criacao_antes": "2 horas",
            "tempo_medio_criacao_depois": "30 minutos",
            "taxa_sucesso_licitacoes": "85%"
        }
    }
    
    return relatorio

def apresentar_resultados(insights, predicoes, relatorio):
    """Apresenta os resultados da demonstração"""
    
    print("📊 ANÁLISE DE SATISFAÇÃO:")
    satisfacao = insights.get("analise_satisfacao", {}).get("geral", {})
    print(f"   • Satisfação Geral: {satisfacao.get('media', 'N/A')}/5 ({satisfacao.get('nivel', 'N/A')})")
    print(f"   • Total de Respostas: {satisfacao.get('total_respostas', 'N/A')}")
    
    print("\n🚨 PRINCIPAIS PROBLEMAS IDENTIFICADOS:")
    problemas = insights.get("problemas_identificados", {})
    for area, count in problemas.get("areas_impacto", {}).items():
        print(f"   • {area}: {count} ocorrências")
    
    print("\n💡 SUGESTÕES PRIORITÁRIAS:")
    sugestoes = insights.get("sugestoes_priorizadas", {})
    for sugestao in sugestoes.get("sugestoes_impacto_alto", [])[:3]:
        print(f"   • {sugestao.get('texto', 'N/A')}")
    
    print("\n🔮 PREDIÇÕES PARA NOVOS EDITAIS:")
    print(f"   • Probabilidade de Sucesso: {predicoes.get('probabilidade_sucesso', 0):.1%}")
    print(f"   • Riscos Identificados: {len(predicoes.get('riscos_identificados', []))}")
    
    print("\n📈 IMPACTO DAS MELHORIAS:")
    metricas = relatorio["metricas_gerais"]
    print(f"   • Satisfação: {metricas['satisfacao_media_antes']} → {metricas['satisfacao_media_depois']} (+{metricas['satisfacao_media_depois'] - metricas['satisfacao_media_antes']:.1f})")
    print(f"   • Tempo de Criação: {metricas['tempo_medio_criacao_antes']} → {metricas['tempo_medio_criacao_depois']}")
    print(f"   • Taxa de Sucesso: {metricas['taxa_sucesso_licitacoes']}")
    
    print("\n🔧 MELHORIAS IMPLEMENTADAS:")
    for melhoria in relatorio["melhorias_implementadas"]:
        print(f"   • {melhoria['titulo']} (ROI: {melhoria['roi_estimado']}x)")
    
    print("\n📋 PRÓXIMAS MELHORIAS:")
    for melhoria in relatorio["melhorias_planejadas"]:
        print(f"   • {melhoria['titulo']} (Prioridade: {melhoria['prioridade']})")

if __name__ == "__main__":
    asyncio.run(main())
