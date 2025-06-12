"""
Orquestrador principal para o processo de geração de editais.
Coordena todos os agentes e tarefas em sequência.
"""

import os
import json
from crewai import Crew, Process
from crewai_agents.edital_agents import EditalAgents
from crewai_agents.edital_tasks import EditalTasks
from api.database import create_db_tables, SessionLocal, EditalRequest, EditalGerado
from api.edital_models import EditalRequest as EditalRequestModel, StatusEdital
from datetime import datetime
import uuid

def run_edital_generation_crew(request_data: dict, user_id: str = "sistema"):
    """
    Função principal que orquestra o processo completo de geração de edital.
    
    Args:
        request_data: Dados da solicitação de edital
        user_id: ID do usuário que solicitou a geração
    
    Returns:
        dict: Resultado completo da geração
    """
    print("🚀 Iniciando processo de geração de edital para os Correios...")
    
    # Garantir que as tabelas existam
    create_db_tables()
    
    # Instanciar agentes e tarefas
    agents = EditalAgents()
    tasks = EditalTasks(agents)
    
    # Gerar ID único para esta solicitação
    request_id = str(uuid.uuid4())
    
    try:
        # === ETAPA 1: COLETA E VALIDAÇÃO DE REQUISITOS ===
        print("\n📋 Etapa 1: Coletando e validando requisitos...")
        
        coletor_agente = agents.coletor_requisitos()
        requisitos_json = json.dumps(request_data, ensure_ascii=False)
        
        coletar_task = tasks.coletar_requisitos_task(
            agent=coletor_agente,
            requisitos_json=requisitos_json
        )
        
        crew_coleta = Crew(
            agents=[coletor_agente],
            tasks=[coletar_task],
            process=Process.sequential,
            verbose=1
        )
        
        resultado_coleta = crew_coleta.kickoff()
        print(f"✅ Requisitos validados: {resultado_coleta}")
        
        # Verificar se requisitos foram aprovados
        try:
            dados_coleta = json.loads(str(resultado_coleta))
            if dados_coleta.get('status') != 'aprovado':
                return {
                    "sucesso": False,
                    "etapa": "validacao_requisitos",
                    "erro": "Requisitos não aprovados",
                    "detalhes": dados_coleta
                }
        except:
            # Se não conseguir parsear, continuar (pode ser formato diferente)
            pass
        
        # === ETAPA 2: ANÁLISES ESPECIALIZADAS ===
        print("\n🔍 Etapa 2: Realizando análises especializadas...")
        
        # Agentes especializados
        juridico_agente = agents.analisador_juridico()
        tecnico_agente = agents.analisador_tecnico()
        financeiro_agente = agents.analisador_financeiro()
        
        # Tarefas de análise (executadas em paralelo)
        juridico_task = tasks.analisar_juridico_task(juridico_agente, str(resultado_coleta))
        tecnico_task = tasks.analisar_tecnico_task(tecnico_agente, str(resultado_coleta))
        financeiro_task = tasks.analisar_financeiro_task(financeiro_agente, str(resultado_coleta))
        
        crew_analises = Crew(
            agents=[juridico_agente, tecnico_agente, financeiro_agente],
            tasks=[juridico_task, tecnico_task, financeiro_task],
            process=Process.sequential,  # Pode ser hierárquico para paralelismo
            verbose=1
        )
        
        resultado_analises = crew_analises.kickoff()
        print(f"✅ Análises especializadas concluídas")
        
        # === ETAPA 3: ANÁLISE DE RISCO CONSOLIDADA ===
        print("\n⚠️ Etapa 3: Calculando risco consolidado...")
        
        risco_agente = agents.especialista_risco()
        
        # Consolidar análises para o cálculo de risco
        analises_consolidadas = {
            "requisitos_validados": str(resultado_coleta),
            "analises_especializadas": str(resultado_analises)
        }
        
        risco_task = tasks.calcular_risco_task(
            agent=risco_agente,
            analises_consolidadas=json.dumps(analises_consolidadas, ensure_ascii=False)
        )
        
        crew_risco = Crew(
            agents=[risco_agente],
            tasks=[risco_task],
            process=Process.sequential,
            verbose=1
        )
        
        resultado_risco = crew_risco.kickoff()
        print(f"✅ Análise de risco concluída")
        
        # === ETAPA 4: GERAÇÃO DO EDITAL ===
        print("\n📝 Etapa 4: Gerando conteúdo do edital...")
        
        gerador_agente = agents.gerador_edital()
        
        # Consolidar todos os dados para geração
        dados_consolidados = {
            "requisitos": request_data,
            "validacao": str(resultado_coleta),
            "analises": str(resultado_analises),
            "risco": str(resultado_risco)
        }
        
        gerar_task = tasks.gerar_edital_task(
            agent=gerador_agente,
            dados_consolidados=json.dumps(dados_consolidados, ensure_ascii=False)
        )
        
        crew_geracao = Crew(
            agents=[gerador_agente],
            tasks=[gerar_task],
            process=Process.sequential,
            verbose=1
        )
        
        resultado_geracao = crew_geracao.kickoff()
        print(f"✅ Edital gerado")
        
        # === ETAPA 5: OTIMIZAÇÃO E REVISÃO ===
        print("\n🔧 Etapa 5: Otimizando edital...")
        
        otimizador_agente = agents.revisor_otimizador()
        
        otimizar_task = tasks.otimizar_edital_task(
            agent=otimizador_agente,
            edital_gerado=str(resultado_geracao)
        )
        
        crew_otimizacao = Crew(
            agents=[otimizador_agente],
            tasks=[otimizar_task],
            process=Process.sequential,
            verbose=1
        )
        
        resultado_otimizacao = crew_otimizacao.kickoff()
        print(f"✅ Edital otimizado")
        
        # === ETAPA 6: COORDENAÇÃO FINAL ===
        print("\n🎯 Etapa 6: Coordenação final...")
        
        coordenador_agente = agents.coordenador_processo()
        
        resultados_completos = {
            "requisitos": request_data,
            "validacao": str(resultado_coleta),
            "analises": str(resultado_analises),
            "risco": str(resultado_risco),
            "edital_gerado": str(resultado_geracao),
            "edital_otimizado": str(resultado_otimizacao)
        }
        
        coordenar_task = tasks.coordenar_processo_task(
            agent=coordenador_agente,
            resultados_completos=json.dumps(resultados_completos, ensure_ascii=False)
        )
        
        crew_coordenacao = Crew(
            agents=[coordenador_agente],
            tasks=[coordenar_task],
            process=Process.sequential,
            verbose=1
        )
        
        resultado_final = crew_coordenacao.kickoff()
        print(f"✅ Processo coordenado e finalizado")
        
        # === ETAPA 7: SALVAMENTO NO BANCO ===
        print("\n💾 Etapa 7: Salvando no banco de dados...")
        
        edital_id = salvar_edital_no_banco(
            request_id=request_id,
            request_data=request_data,
            resultado_final=str(resultado_final),
            user_id=user_id
        )
        
        print(f"✅ Edital salvo com ID: {edital_id}")
        
        # === RESULTADO FINAL ===
        resultado_completo = {
            "sucesso": True,
            "edital_id": edital_id,
            "request_id": request_id,
            "etapas_executadas": [
                "validacao_requisitos",
                "analises_especializadas", 
                "calculo_risco",
                "geracao_edital",
                "otimizacao",
                "coordenacao_final",
                "salvamento"
            ],
            "resultado_final": str(resultado_final),
            "data_processamento": datetime.now().isoformat()
        }
        
        print("\n🎉 Processo de geração de edital concluído com sucesso!")
        return resultado_completo
        
    except Exception as e:
        print(f"\n❌ Erro durante o processo: {str(e)}")
        return {
            "sucesso": False,
            "erro": str(e),
            "request_id": request_id,
            "data_erro": datetime.now().isoformat()
        }

def salvar_edital_no_banco(request_id: str, request_data: dict, resultado_final: str, user_id: str) -> str:
    """
    Salva o edital gerado no banco de dados.
    
    Args:
        request_id: ID da solicitação
        request_data: Dados originais da solicitação
        resultado_final: Resultado final do processo
        user_id: ID do usuário
    
    Returns:
        str: ID do edital salvo
    """
    db = SessionLocal()
    
    try:
        # Gerar ID único para o edital
        edital_id = str(uuid.uuid4())
        
        # Salvar solicitação original
        edital_request = EditalRequest(
            id=request_id,
            objeto=request_data.get('objeto', ''),
            tipo_licitacao=request_data.get('tipo_licitacao', ''),
            modalidade=request_data.get('modalidade', ''),
            categoria=request_data.get('categoria', ''),
            setor_requisitante=request_data.get('setor_requisitante', {}),
            itens=request_data.get('itens', []),
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
            status="concluido"
        )
        
        db.add(edital_request)
        
        # Extrair dados do resultado final (tentar parsear JSON)
        try:
            dados_resultado = json.loads(resultado_final)
            conteudo_edital = dados_resultado.get('conteudo_edital', resultado_final)
        except:
            conteudo_edital = resultado_final
        
        # Salvar edital gerado
        edital_gerado = EditalGerado(
            id=edital_id,
            request_id=request_id,
            analise_juridica={"status": "analisado"},  # Placeholder
            analise_tecnica={"status": "analisado"},   # Placeholder
            analise_financeira={"status": "analisado"}, # Placeholder
            analise_risco={"status": "analisado"},     # Placeholder
            conteudo_edital=conteudo_edital,
            status="rascunho",
            criado_por=user_id
        )
        
        db.add(edital_gerado)
        db.commit()
        
        return edital_id
        
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    # Exemplo de uso para teste
    exemplo_request = {
        "objeto": "Contratação de serviços de limpeza",
        "tipo_licitacao": "pregao",
        "modalidade": "eletronica",
        "categoria": "servicos",
        "setor_requisitante": {
            "nome": "Gerência de Facilities",
            "responsavel": "João Silva",
            "email": "joao.silva@correios.com.br",
            "justificativa": "Necessidade de manutenção da limpeza predial"
        },
        "itens": [
            {
                "numero": 1,
                "descricao": "Serviços de limpeza predial",
                "unidade": "m²",
                "quantidade": 1000,
                "categoria": "servicos"
            }
        ],
        "valor_total_estimado": 50000.0,
        "prazo_execucao": 365,
        "prazo_proposta": 10
    }
    
    resultado = run_edital_generation_crew(exemplo_request, "teste")
    print(f"\nResultado final: {json.dumps(resultado, indent=2, ensure_ascii=False)}")
