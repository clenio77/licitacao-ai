from crewai import Agent
from crewai_agents.tools import (
    BuscarNovasLicitacoesTool, BaixarEditalTool, ExtrairTextoDocumentoTool, SalvarDadosLicitacaoTool,
    ConsultarLei14133Tool, ConsultarPrecosReferenciaTool, PesquisarPrecoWebTool, ObterCotacaoCambialTool,
    GerarMinutaDocumentoTool, EnviarEmailNotificacaoTool, EnviarMensagemTeamsTool,
    _LEI_14133_CONTENT, _PRECOS_REFERENCIA
)
from dotenv import load_dotenv
import os
from textwrap import dedent
from crewai_tools import ScrapeWebsiteTool

# Integração com LlamaIndex
from llama_index.llms.llama_cpp import LlamaCPP

load_dotenv()

class CustomLLM_LlamaIndex:
    """
    Wrapper para CrewAI usar LlamaIndex (LlamaCPP) como LLM local.
    Permite que os agentes CrewAI utilizem um modelo open source local ao invés de OpenAI.
    """
    def __init__(self, model_path=None):
        # Caminho do modelo Llama local
        self.model_path = model_path or os.getenv("LLAMA_MODEL_PATH", "./models/llama-2-7b-chat.ggmlv3.q4_0.bin")
        # Instancia o modelo LlamaCPP
        self.llm = LlamaCPP(
            model_path=self.model_path,
            temperature=0.7,
            max_new_tokens=256,
        )

    def chat_completion(self, messages, temperature, max_tokens):
        """
        Recebe uma lista de mensagens (como no formato OpenAI) e retorna a resposta do modelo Llama.
        Args:
            messages (list): Lista de dicionários com chaves 'role' e 'content'.
            temperature (float): Temperatura do modelo.
            max_tokens (int): Máximo de tokens na resposta.
        Returns:
            str: Resposta do modelo Llama.
        """
        # Concatena as mensagens para um único prompt
        prompt = "\n".join([m.get("content", "") for m in messages])
        response = self.llm.complete(prompt)
        return response

# Instância global do LLM para os agentes
llm_instance = CustomLLM_LlamaIndex()

class LicitacaoAgents:
    """
    Classe que centraliza a criação dos agentes CrewAI para o fluxo de licitações.
    Cada método retorna um agente especializado em uma etapa do processo.
    """
    def __init__(self):
        # Ferramentas customizadas para cada agente
        self.buscar_licitacoes_tool = BuscarNovasLicitacoesTool()
        self.baixar_edital_tool = BaixarEditalTool()
        self.extrair_texto_tool = ExtrairTextoDocumentoTool()
        self.salvar_dados_tool = SalvarDadosLicitacaoTool()
        self.consultar_lei_tool = ConsultarLei14133Tool()
        self.consultar_precos_tool = ConsultarPrecosReferenciaTool()
        self.pesquisar_preco_tool = PesquisarPrecoWebTool()
        self.cotacao_cambial_tool = ObterCotacaoCambialTool()
        self.gerar_minuta_tool = GerarMinutaDocumentoTool()
        self.enviar_email_tool = EnviarEmailNotificacaoTool()
        self.enviar_teams_tool = EnviarMensagemTeamsTool()
        # LLM local (LlamaIndex)
        self.llm = llm_instance

    def coletor_de_editais(self):
        """
        Agente responsável por buscar novas licitações e baixar editais.
        Usa ferramentas de scraping e download.
        """
        return Agent(
            role='Coletor de Editais',
            goal='Encontrar novas licitações no portal Comprasnet e baixar seus editais.',
            backstory="Sou especialista em web scraping e monitoramento de portais governamentais, garantindo que nenhum edital importante seja perdido.",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[self.buscar_licitacoes_tool, self.baixar_edital_tool]
        )

    def analisador_basico_de_edital(self):
        """
        Agente que extrai os principais campos e gera um resumo do edital.
        """
        return Agent(
            role='Analisador Básico de Edital',
            goal='Extrair os 5-7 campos-chave mais críticos de um edital e gerar um resumo conciso.',
            backstory="Com foco em eficiência, identifico rapidamente as informações essenciais de qualquer edital, transformando texto complexo em dados acionáveis.",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[self.extrair_texto_tool]
        )

    def avaliador_juridico(self):
        """
        Agente especialista em direito administrativo, avalia conformidade jurídica do edital.
        """
        return Agent(
            role='Avaliador Jurídico',
            goal=dedent("""
                Analisar o edital da licitação sob a ótica da Lei nº 14.133/2021.
                Identificar possíveis não-conformidades, cláusulas ambíguas ou riscos jurídicos.
                Deve focar em princípios gerais e requisitos de habilitação.
                """),
            backstory=dedent("""
                Sou um especialista em direito administrativo e licitações, focado na Lei 14.133/2021.
                Minha função é garantir a conformidade jurídica dos processos licitatórios.
                """),
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[self.consultar_lei_tool]
        )

    def analisador_de_mercado(self):
        """
        Agente que pesquisa preços de referência, dados de mercado e avalia viabilidade econômica.
        """
        return Agent(
            role='Analisador de Mercado e Precificação',
            goal=dedent("""
                Pesquisar e analisar dados de mercado e preços de referência para o objeto da licitação.
                Avaliar a viabilidade econômica, sugerir um preço de referência ou faixa de preço,
                e considerar a variação cambial se o objeto sugerir compra internacional.
                """),
            backstory=dedent("""
                Sou um analista de mercado com experiência em compras públicas.
                Minha expertise é encontrar as melhores informações de preço e viabilidade econômica,
                incluindo fatores como cotações de moedas internacionais.
                """),
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[self.consultar_precos_tool, self.pesquisar_preco_tool, self.cotacao_cambial_tool]
        )
    
    def gerador_de_documentos(self):
        """
        Agente responsável por gerar minutas e documentos a partir dos dados processados.
        """
        return Agent(
            role='Gerador de Documentos',
            goal=dedent("""
                Gerar minutas de documentos com base nas informações processadas da licitação.
                Isso pode incluir relatórios de análise, checklists ou minutas de comunicados.
                """),
            backstory=dedent("""
                Sou um redator técnico e especialista em automação de documentos.
                Transformo dados brutos em documentos claros e formatados.
                """),
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[self.gerar_minuta_tool]
        )

    def gerente_de_processo(self):
        """
        Agente que consolida todas as análises e recomendações, avalia risco e gera recomendação final.
        """
        return Agent(
            role='Gerente de Processos de Licitação',
            goal=dedent("""
                Consolidar todas as análises (básica, jurídica, de mercado) de uma licitação,
                avaliar o risco geral e determinar um status de recomendação final.
                Deve produzir um JSON consolidado com todos os dados e um campo de recomendação.
                Além disso, deve enviar notificações quando necessário.
                """),
            backstory=dedent("""
                Sou o elo central da equipe, responsável por integrar as informações
                dos especialistas e fornecer uma visão unificada e uma recomendação clara
                para a tomada de decisão estratégica, além de alertar sobre riscos.
                """),
            verbose=True,
            allow_delegation=True,
            llm=self.llm,
            tools=[self.enviar_email_tool, self.enviar_teams_tool]
        )

    def estruturador_de_dados(self):
        """
        Agente que consolida e formata os dados extraídos das licitações para uso posterior.
        """
        return Agent(
            role='Estruturador de Dados de Licitações',
            goal='Consolidar e formatar os dados extraídos das licitações em um arquivo JSON padronizado para consumo posterior.',
            backstory="Minha missão é garantir que todos os dados coletados e analisados estejam organizados e prontos para serem usados em relatórios e dashboards.",
            verbose=True,
            allow_delegation=False,
            llm=self.llm,
            tools=[self.salvar_dados_tool]
        )