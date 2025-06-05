# Orquestrador CrewAI para licitações
# Agora utiliza LlamaIndex (LlamaCPP) como LLM local para prototipação.
# Não depende mais de OpenAI.

from crewai import Crew, Process
from crewai_agents.agents import LicitacaoAgents
from crewai_agents.tasks import LicitacaoTasks
import json
import os
from dotenv import load_dotenv
from api.database import create_db_tables
from datetime import datetime

load_dotenv()

def run_licitacao_crew():
    """
    Função principal que orquestra o fluxo de processamento de licitações usando CrewAI.
    Executa as etapas: busca, download, análise, avaliação jurídica, análise de mercado, consolidação e salvamento.
    """
    print("Iniciando a Crew de Gestão de Licitações (com todos os agentes e gerente)...")

    # Garante que as tabelas do DB existam
    create_db_tables()

    # Instancia os agentes e as tarefas
    agents = LicitacaoAgents()  # Classe que centraliza todos os agentes
    tasks = LicitacaoTasks(agents)  # Classe que centraliza todas as tarefas

    # Define os agentes especializados
    coletor_agente = agents.coletor_de_editais()  # Busca e baixa editais
    analisador_agente = agents.analisador_basico_de_edital()  # Extrai campos principais
    avaliador_juridico_agente = agents.avaliador_juridico()  # Avalia conformidade jurídica
    analisador_mercado_agente = agents.analisador_de_mercado()  # Pesquisa preços e mercado
    gerente_agente = agents.gerente_de_processo()  # Consolida e recomenda
    estruturador_agente = agents.estruturador_de_dados()  # Salva dados estruturados

    # URL do Comprasnet (pode ser customizada por variável de ambiente)
    comprasnet_search_url = os.getenv("COMPRASNET_SEARCH_URL", "https://www.comprasnet.gov.br/seguro/indexportal.asp")

    # Passo 1: O Coletor busca novas licitações
    print("\n--- Passo 1: Coletor buscando novas licitações no Comprasnet ---")
    buscar_licitacoes_task = tasks.buscar_licitacoes_task(
        agent=coletor_agente,
        search_url=comprasnet_search_url
    )

    # Cria uma Crew temporária para apenas a primeira tarefa de busca
    crew_busca = Crew(
        agents=[coletor_agente],
        tasks=[buscar_licitacoes_task],
        process=Process.sequential,
        verbose=1,
        full_output=True
    )

    # Executa a busca
    result_busca = crew_busca.kickoff()
    
    # Tenta parsear o resultado da busca
    licitacoes_encontradas_str = result_busca['final_output'].raw_output
    licitacoes_encontradas = []
    try:
        # A ferramenta retorna um JSON string, então precisamos parsear
        licitacoes_encontradas = json.loads(licitacoes_encontradas_str)
    except json.JSONDecodeError:
        print(f"Erro ao parsear JSON da busca: {licitacoes_encontradas_str}. Nenhuma licitação para processar.")
        return # Sai se não houver licitações válidas

    if not licitacoes_encontradas:
        print("Nenhuma nova licitação encontrada para processamento.")
        return

    print(f"\n--- {len(licitacoes_encontradas)} Novas licitações identificadas para processamento ---")

    # Loop para processar cada licitação encontrada
    for licitacao_info in licitacoes_encontradas:
        licitacao_id = licitacao_info.get('id')
        licitacao_url = licitacao_info.get('url')
        
        if not licitacao_id or not licitacao_url:
            print(f"Aviso: Informação inválida para licitação: {licitacao_info}. Pulando.")
            continue

        print(f"\n--- Processando Licitação ID: {licitacao_id}, URL: {licitacao_url} ---")

        # Tarefa 2: Baixar e Extrair Texto do Edital
        # IMPORTANTE: A ferramenta 'baixar_edital' no MVP ainda baixa para o disco local.
        baixar_e_extrair_task = tasks.baixar_e_extrair_edital_task(
            agent=coletor_agente, # Coletor para baixar e extrair
            licitacao_url=licitacao_url # URL do edital real
        )
        baixar_e_extrair_task.human_input = False # Não precisa de input humano para esta tarefa

        # Tarefa 3: Analisar o Edital (básico)
        analisar_task = tasks.analisar_edital_basico_task(
            agent=analisador_agente,
            edital_content=baixar_e_extrair_task.output, # Output da tarefa anterior é o input
            licitacao_url=licitacao_url # Passa a URL original para o JSON final
        )
        analisar_task.human_input = False # Não precisa de input humano

        # Tarefa 4: Avaliar Conformidade Jurídica
        avaliar_juridica_task = tasks.avaliar_conformidade_juridica_task(
            agent=avaliador_juridico_agente,
            edital_content=baixar_e_extrair_task.output, # Texto do edital
            licitacao_data_json=analisar_task.output # JSON da análise básica
        )
        avaliar_juridica_task.human_input = False

        # Tarefa 5: Analisar Mercado
        analisar_mercado_task = tasks.analisar_mercado_task(
            agent=analisador_mercado_agente,
            licitacao_data_json=avaliar_juridica_task.output # JSON com análise básica e jurídica
        )
        analisar_mercado_task.human_input = False

        # Tarefa 6: Consolidar e Recomendar (Pelo Gerente)
        consolidar_e_recomendar_task = tasks.consolidar_e_recomendar_task(
            agent=gerente_agente,
            licitacao_data_json=analisar_mercado_task.output # Recebe o JSON completo
        )
        consolidar_e_recomendar_task.human_input = False

        # Tarefa 7: Salvar os Dados no DB (agora com recomendação do gerente)
        salvar_task = tasks.salvar_dados_task(
            agent=estruturador_agente,
            data_json=consolidar_e_recomendar_task.output # JSON final do gerente
        )
        salvar_task.human_input = False

        # Cria a Crew para processar a licitação completa
        crew_processamento_licitacao = Crew(
            agents=[
                coletor_agente,
                analisador_agente,
                avaliador_juridico_agente,
                analisador_mercado_agente,
                gerente_agente, # Incluir o gerente aqui
                estruturador_agente
            ],
            tasks=[
                baixar_e_extrair_task,
                analisar_task,
                avaliar_juridica_task,
                analisar_mercado_task,
                consolidar_e_recomendar_task, # Incluir a tarefa do gerente
                salvar_task
            ],
            process=Process.sequential,
            verbose=2, # Nível de detalhe da execução
            full_output=True,
            max_rpm=29 # Limita as requisições por minuto ao LLM para evitar exceder cotas
        )

        try:
            licitacao_result = crew_processamento_licitacao.kickoff()
            print(f"Processamento da licitação {licitacao_id} concluído.")
            print(licitacao_result['final_output'].raw_output)
        except Exception as e:
            print(f"Erro ao processar licitação {licitacao_id}: {e}")

if __name__ == "__main__":
    # Garante que as pastas de dados existam
    os.makedirs("backend/data/raw_licitacoes", exist_ok=True)
    os.makedirs("backend/data/generated_documents", exist_ok=True)
    os.makedirs("backend/data/", exist_ok=True) # Para lei e preços

    # Para um MVP simples, podemos rodar uma vez ou em um loop básico
    # Para produção, use um scheduler (cron/systemd timer/Kubernetes CronJob)
    print("Executando a Crew de licitações. Isto deve ser agendado externamente em produção.")
    run_licitacao_crew()