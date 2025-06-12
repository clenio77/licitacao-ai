"""
Agentes CrewAI especializados na geração de editais de licitação.
Cada agente tem uma responsabilidade específica no processo de geração.
"""

from crewai import Agent
from crewai_agents.edital_tools import (
    AnalisarRequisitosTool, ConsultarHistoricoTool, GerarEditalTool,
    ValidarConformidadeTool, CalcularRiscoTool, OtimizarEditalTool,
    ConsultarTemplatesTool, AnalisarMercadoTool
)
from crewai_agents.knowledge_base_tools import (
    KnowledgeBaseTool, ScrapingSchedulerTool, KnowledgeBaseAnalyticsTool
)
from crewai_agents.feedback_analysis_tools import (
    FeedbackAnalysisTool, FeedbackPredictionTool
)
from dotenv import load_dotenv
import os
from textwrap import dedent

# Integração com LlamaIndex (mesmo LLM dos agentes existentes)
from crewai_agents.llamaindex_utils import llm_instance

load_dotenv()

class EditalAgents:
    """
    Classe que centraliza a criação dos agentes CrewAI para geração de editais.
    Cada agente é especializado em uma etapa específica do processo.
    """
    
    def __init__(self):
        # Ferramentas especializadas para geração de editais
        self.analisar_requisitos_tool = AnalisarRequisitosTool()
        self.consultar_historico_tool = ConsultarHistoricoTool()
        self.gerar_edital_tool = GerarEditalTool()
        self.validar_conformidade_tool = ValidarConformidadeTool()
        self.calcular_risco_tool = CalcularRiscoTool()
        self.otimizar_edital_tool = OtimizarEditalTool()
        self.consultar_templates_tool = ConsultarTemplatesTool()
        self.analisar_mercado_tool = AnalisarMercadoTool()

        # Ferramentas da base de conhecimento
        self.knowledge_base_tool = KnowledgeBaseTool()
        self.scraping_scheduler_tool = ScrapingSchedulerTool()
        self.knowledge_analytics_tool = KnowledgeBaseAnalyticsTool()

        # Ferramentas de análise de feedback
        self.feedback_analysis_tool = FeedbackAnalysisTool()
        self.feedback_prediction_tool = FeedbackPredictionTool()

        # LLM compartilhado
        self.llm = llm_instance

    def coletor_requisitos(self):
        """
        Agente responsável por coletar e validar os requisitos de entrada.
        Analisa a solicitação da equipe de compras e identifica informações faltantes.
        """
        return Agent(
            role='Coletor de Requisitos',
            goal=dedent("""
                Analisar e validar os requisitos fornecidos pela equipe de compras.
                Identificar informações faltantes ou inconsistentes.
                Garantir que todos os dados necessários estejam completos e corretos.
            """),
            backstory=dedent("""
                Sou especialista em análise de requisitos para licitações dos Correios.
                Tenho experiência em identificar lacunas em especificações e garantir
                que todas as informações necessárias estejam presentes antes de
                iniciar o processo de geração do edital.
            """),
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[self.analisar_requisitos_tool]
        )

    def analisador_juridico(self):
        """
        Agente especializado em análise jurídica e conformidade legal.
        Verifica conformidade com Lei 14.133/2021 e outras normas aplicáveis.
        """
        return Agent(
            role='Analisador Jurídico',
            goal=dedent("""
                Analisar a conformidade jurídica dos requisitos e especificações.
                Verificar adequação à Lei 14.133/2021 e demais normas aplicáveis.
                Identificar riscos jurídicos e sugerir melhorias para mitigar fracassos.
            """),
            backstory=dedent("""
                Sou especialista em direito administrativo e licitações públicas.
                Conheço profundamente a Lei 14.133/2021 e tenho experiência em
                identificar cláusulas que podem causar impugnações ou fracassos
                em licitações dos Correios.
            """),
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[self.validar_conformidade_tool, self.consultar_historico_tool, self.knowledge_base_tool]
        )

    def analisador_tecnico(self):
        """
        Agente especializado em análise técnica de especificações.
        Avalia viabilidade técnica e adequação das especificações.
        """
        return Agent(
            role='Analisador Técnico',
            goal=dedent("""
                Analisar a viabilidade técnica das especificações.
                Verificar se os requisitos técnicos são adequados e exequíveis.
                Identificar especificações que podem limitar a competitividade.
            """),
            backstory=dedent("""
                Sou especialista técnico com experiência em especificações para
                licitações dos Correios. Conheço o mercado fornecedor e sei
                identificar especificações que podem causar fracassos por
                limitarem excessivamente a participação ou serem inexequíveis.
            """),
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[self.analisar_requisitos_tool, self.consultar_historico_tool, self.knowledge_base_tool]
        )

    def analisador_financeiro(self):
        """
        Agente especializado em análise financeira e de mercado.
        Avalia valores estimados e condições financeiras.
        """
        return Agent(
            role='Analisador Financeiro',
            goal=dedent("""
                Analisar a adequação dos valores estimados e condições financeiras.
                Verificar se os valores estão compatíveis com o mercado.
                Identificar riscos financeiros que podem causar fracassos.
            """),
            backstory=dedent("""
                Sou especialista em análise financeira e de mercado para licitações.
                Tenho experiência em pesquisa de preços e conheço os fatores que
                podem tornar uma licitação financeiramente inviável ou pouco
                atrativa para os fornecedores.
            """),
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[self.analisar_mercado_tool, self.consultar_historico_tool, self.knowledge_base_tool]
        )

    def especialista_risco(self):
        """
        Agente especializado em análise e mitigação de riscos.
        Consolida análises e identifica fatores de risco para fracasso.
        """
        return Agent(
            role='Especialista em Riscos',
            goal=dedent("""
                Consolidar todas as análises e identificar fatores de risco.
                Calcular probabilidade de sucesso baseada no histórico.
                Sugerir medidas de mitigação para reduzir riscos de fracasso.
            """),
            backstory=dedent("""
                Sou especialista em gestão de riscos para licitações públicas.
                Analiso históricos de sucessos e fracassos para identificar
                padrões e fatores críticos. Minha expertise ajuda a prever
                e mitigar riscos que podem levar ao fracasso de licitações.
            """),
            verbose=True,
            allow_delegation=True,
            llm=self.llm,
            tools=[self.calcular_risco_tool, self.consultar_historico_tool, self.knowledge_base_tool]
        )

    def especialista_conhecimento(self):
        """
        Agente especializado em consultar e aplicar conhecimento de licitações bem-sucedidas.
        Utiliza base de conhecimento coletada via web scraping.
        """
        return Agent(
            role='Especialista em Base de Conhecimento',
            goal=dedent("""
                Consultar base de conhecimento de licitações bem-sucedidas similares.
                Extrair boas práticas, padrões de sucesso e recomendações específicas.
                Aplicar aprendizados de casos similares para otimizar o edital atual.
            """),
            backstory=dedent("""
                Sou especialista em análise de dados de licitações públicas.
                Tenho acesso a uma vasta base de conhecimento de licitações
                bem-sucedidas coletadas de sites governamentais. Minha expertise
                está em identificar padrões de sucesso e aplicar essas lições
                para maximizar as chances de sucesso de novas licitações.
            """),
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[self.knowledge_base_tool, self.knowledge_analytics_tool]
        )

    def analista_feedback(self):
        """
        Agente especializado em análise de feedback e melhoria contínua.
        Processa feedback de stakeholders e identifica oportunidades de melhoria.
        """
        return Agent(
            role='Analista de Feedback e Melhoria Contínua',
            goal=dedent("""
                Analisar feedback de setores requisitantes, empresas licitantes e setor de licitação.
                Identificar padrões, problemas recorrentes e oportunidades de melhoria.
                Gerar insights acionáveis para aprimorar continuamente o sistema.
            """),
            backstory=dedent("""
                Sou especialista em análise de feedback e melhoria contínua de processos.
                Tenho experiência em processar grandes volumes de feedback qualitativo
                e quantitativo, identificando padrões e tendências que não são óbvios.
                Minha expertise está em transformar feedback em ações concretas de melhoria.
            """),
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[self.feedback_analysis_tool, self.feedback_prediction_tool]
        )

    def gerador_edital(self):
        """
        Agente responsável por gerar o conteúdo do edital.
        Utiliza templates e aplica as melhorias sugeridas pelas análises.
        """
        return Agent(
            role='Gerador de Edital',
            goal=dedent("""
                Gerar o conteúdo completo do edital baseado nos requisitos
                e nas análises realizadas. Aplicar melhorias sugeridas pelos
                especialistas para maximizar as chances de sucesso.
            """),
            backstory=dedent("""
                Sou especialista na redação de editais de licitação para os Correios.
                Conheço os templates padrão e sei como adaptá-los baseado nas
                análises dos especialistas. Meu objetivo é gerar editais que
                sejam claros, completos e tenham alta probabilidade de sucesso.
            """),
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[self.gerar_edital_tool, self.consultar_templates_tool]
        )

    def revisor_otimizador(self):
        """
        Agente responsável por revisar e otimizar o edital gerado.
        Aplica melhorias finais baseadas no histórico e boas práticas.
        """
        return Agent(
            role='Revisor e Otimizador',
            goal=dedent("""
                Revisar o edital gerado e aplicar otimizações finais.
                Verificar consistência, clareza e completude.
                Aplicar lições aprendidas do histórico para maximizar sucesso.
            """),
            backstory=dedent("""
                Sou revisor sênior especializado em editais de licitação.
                Tenho vasta experiência em identificar problemas que podem
                causar fracassos e sei como otimizar editais baseado em
                lições aprendidas de casos anteriores dos Correios.
            """),
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[self.otimizar_edital_tool, self.consultar_historico_tool]
        )

    def coordenador_processo(self):
        """
        Agente coordenador que gerencia todo o processo de geração.
        Consolida resultados e toma decisões sobre o fluxo.
        """
        return Agent(
            role='Coordenador do Processo',
            goal=dedent("""
                Coordenar todo o processo de geração do edital.
                Consolidar os resultados de todas as análises.
                Tomar decisões sobre aprovação, rejeição ou necessidade de ajustes.
                Gerar relatório final com justificativas e recomendações.
            """),
            backstory=dedent("""
                Sou o coordenador responsável por todo o processo de geração
                de editais nos Correios. Tenho visão holística do processo
                e experiência para tomar decisões baseadas nas análises dos
                especialistas. Meu objetivo é garantir editais de alta qualidade
                que minimizem riscos de fracasso.
            """),
            verbose=True,
            allow_delegation=True,
            llm=self.llm,
            tools=[self.calcular_risco_tool, self.consultar_historico_tool]
        )
