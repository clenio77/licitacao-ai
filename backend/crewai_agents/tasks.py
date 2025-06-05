# tasks.py - Define as tarefas (Tasks) que os agentes CrewAI executam no fluxo de licitações.
# Cada função/método representa uma etapa do processamento de uma licitação.

from crewai import Task
from textwrap import dedent

class LicitacaoTasks:
    """
    Classe que centraliza a criação das tarefas (Tasks) CrewAI para o fluxo de licitações.
    Cada método retorna uma Task configurada para um agente específico.
    """
    def __init__(self, agents):
        """
        Inicializa a classe com os agentes já instanciados.
        Args:
            agents: Instância de LicitacaoAgents com todos os agentes necessários.
        """
        self.agents = agents

    def buscar_licitacoes_task(self, agent, search_url):
        """
        Tarefa para buscar novas licitações em um portal (ex: Comprasnet).
        Args:
            agent: Agente responsável pela busca.
            search_url (str): URL do portal de busca.
        Returns:
            Task: Tarefa configurada para busca de licitações.
        """
        return Task(
            description=dedent(f"""
                Buscar novas licitações no portal: {search_url}.
                Retornar uma lista de licitações encontradas em formato JSON.
            """),
            agent=agent,
            expected_output="JSON com lista de licitações (id, url, objeto, etc)."
        )

    def baixar_e_extrair_edital_task(self, agent, licitacao_url):
        """
        Tarefa para baixar o edital e extrair seu texto.
        Args:
            agent: Agente responsável pelo download e extração.
            licitacao_url (str): URL do edital.
        Returns:
            Task: Tarefa configurada para baixar e extrair edital.
        """
        return Task(
            description=dedent(f"""
                Baixar o edital da licitação na URL: {licitacao_url}.
                Extrair o texto completo do documento (PDF, DOCX, etc).
            """),
            agent=agent,
            expected_output="Texto completo do edital extraído."
        )

    def analisar_edital_basico_task(self, agent, edital_content, licitacao_url):
        """
        Tarefa para analisar o edital e extrair campos principais.
        Args:
            agent: Agente responsável pela análise.
            edital_content (str): Texto do edital.
            licitacao_url (str): URL do edital.
        Returns:
            Task: Tarefa configurada para análise básica do edital.
        """
        return Task(
            description=dedent(f"""
                Analisar o texto do edital extraído.
                Extrair os principais campos (objeto, data, valor, requisitos, etc).
                Gerar um resumo estruturado em JSON.
                URL do edital: {licitacao_url}
            """),
            agent=agent,
            input_data=edital_content,
            expected_output="JSON com campos extraídos e resumo."
        )

    def avaliar_conformidade_juridica_task(self, agent, edital_content, licitacao_data_json):
        """
        Tarefa para avaliar a conformidade jurídica do edital.
        Args:
            agent: Agente jurídico.
            edital_content (str): Texto do edital.
            licitacao_data_json (str): JSON com análise básica.
        Returns:
            Task: Tarefa configurada para avaliação jurídica.
        """
        return Task(
            description=dedent(f"""
                Avaliar a conformidade jurídica do edital com base na Lei 14.133/2021.
                Identificar riscos, cláusulas ambíguas e pontos de atenção.
                Utilizar o texto do edital e o JSON da análise básica.
            """),
            agent=agent,
            input_data={"edital": edital_content, "analise_basica": licitacao_data_json},
            expected_output="JSON com análise jurídica, riscos e recomendações."
        )

    def analisar_mercado_task(self, agent, licitacao_data_json):
        """
        Tarefa para analisar o mercado e sugerir preços de referência.
        Args:
            agent: Agente de mercado.
            licitacao_data_json (str): JSON com análise jurídica e básica.
        Returns:
            Task: Tarefa configurada para análise de mercado.
        """
        return Task(
            description=dedent(f"""
                Analisar dados de mercado e sugerir preços de referência para a licitação.
                Considerar histórico, cotações, variação cambial e contexto econômico.
                Utilizar o JSON consolidado das análises anteriores.
            """),
            agent=agent,
            input_data=licitacao_data_json,
            expected_output="JSON com análise de mercado e sugestão de preço."
        )

    def consolidar_e_recomendar_task(self, agent, licitacao_data_json):
        """
        Tarefa para consolidar todas as análises e gerar recomendação final.
        Args:
            agent: Gerente de processo.
            licitacao_data_json (str): JSON consolidado das análises.
        Returns:
            Task: Tarefa configurada para consolidação e recomendação.
        """
        return Task(
            description=dedent(f"""
                Consolidar todas as análises (básica, jurídica, mercado).
                Avaliar risco geral e gerar recomendação final para a licitação.
                Gerar um JSON final com todos os dados e recomendação.
            """),
            agent=agent,
            input_data=licitacao_data_json,
            expected_output="JSON final consolidado com recomendação."
        )

    def salvar_dados_task(self, agent, data_json):
        """
        Tarefa para salvar os dados da licitação no banco de dados.
        Args:
            agent: Estruturador de dados.
            data_json (str): JSON final consolidado.
        Returns:
            Task: Tarefa configurada para salvar dados.
        """
        return Task(
            description=dedent(f"""
                Salvar os dados consolidados da licitação no banco de dados.
                Garantir que todas as informações estejam estruturadas corretamente.
            """),
            agent=agent,
            input_data=data_json,
            expected_output="Confirmação de salvamento no banco."
        )