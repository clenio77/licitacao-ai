"""
Tarefas (Tasks) CrewAI para o processo de geração de editais.
Define o fluxo sequencial de análise e geração.
"""

from crewai import Task
from textwrap import dedent

class EditalTasks:
    """
    Classe que centraliza a criação das tarefas para geração de editais.
    Cada tarefa representa uma etapa do processo de geração.
    """
    
    def __init__(self, agents):
        """
        Inicializa com os agentes já instanciados.
        Args:
            agents: Instância de EditalAgents com todos os agentes
        """
        self.agents = agents

    def coletar_requisitos_task(self, agent, requisitos_json):
        """
        Tarefa para coletar e validar requisitos de entrada.
        Args:
            agent: Agente coletor de requisitos
            requisitos_json: JSON com requisitos fornecidos
        Returns:
            Task: Tarefa configurada para coleta de requisitos
        """
        return Task(
            description=dedent(f"""
                Analisar e validar os requisitos fornecidos pela equipe de compras dos Correios.
                
                REQUISITOS RECEBIDOS:
                {requisitos_json}
                
                AÇÕES A EXECUTAR:
                1. Verificar completude dos dados obrigatórios
                2. Identificar inconsistências ou lacunas
                3. Validar coerência entre tipo de licitação, categoria e valores
                4. Sugerir melhorias nos requisitos
                5. Classificar complexidade da licitação
                
                RESULTADO ESPERADO:
                JSON com status da validação, problemas identificados, sugestões de melhoria
                e classificação de complexidade.
            """),
            agent=agent,
            expected_output="JSON estruturado com análise completa dos requisitos de entrada."
        )

    def analisar_juridico_task(self, agent, requisitos_validados):
        """
        Tarefa para análise jurídica e conformidade legal.
        Args:
            agent: Agente analisador jurídico
            requisitos_validados: Resultado da validação de requisitos
        Returns:
            Task: Tarefa configurada para análise jurídica
        """
        return Task(
            description=dedent(f"""
                Realizar análise jurídica completa dos requisitos para garantir conformidade
                com a Lei 14.133/2021 e demais normas aplicáveis.
                
                DADOS DE ENTRADA:
                {requisitos_validados}
                
                AÇÕES A EXECUTAR:
                1. Verificar adequação do tipo de licitação ao objeto e valor
                2. Validar prazos conforme legislação vigente
                3. Analisar requisitos de habilitação
                4. Identificar cláusulas que podem gerar impugnações
                5. Consultar histórico de fracassos por motivos jurídicos
                6. Sugerir ajustes para mitigar riscos jurídicos
                
                RESULTADO ESPERADO:
                JSON com análise de conformidade, pontos de atenção, sugestões de melhoria
                e classificação de risco jurídico.
            """),
            agent=agent,
            expected_output="JSON com análise jurídica completa e classificação de risco."
        )

    def analisar_tecnico_task(self, agent, requisitos_validados):
        """
        Tarefa para análise técnica das especificações.
        Args:
            agent: Agente analisador técnico
            requisitos_validados: Resultado da validação de requisitos
        Returns:
            Task: Tarefa configurada para análise técnica
        """
        return Task(
            description=dedent(f"""
                Realizar análise técnica das especificações para garantir viabilidade
                e adequação ao mercado fornecedor.
                
                DADOS DE ENTRADA:
                {requisitos_validados}
                
                AÇÕES A EXECUTAR:
                1. Avaliar viabilidade técnica das especificações
                2. Verificar se especificações não são restritivas demais
                3. Analisar adequação dos requisitos técnicos ao objeto
                4. Consultar histórico de fracassos por motivos técnicos
                5. Identificar especificações que podem limitar competitividade
                6. Sugerir ajustes para melhorar participação
                
                RESULTADO ESPERADO:
                JSON com análise de viabilidade técnica, pontos de atenção,
                sugestões de melhoria e classificação de risco técnico.
            """),
            agent=agent,
            expected_output="JSON com análise técnica completa e recomendações."
        )

    def analisar_financeiro_task(self, agent, requisitos_validados):
        """
        Tarefa para análise financeira e de mercado.
        Args:
            agent: Agente analisador financeiro
            requisitos_validados: Resultado da validação de requisitos
        Returns:
            Task: Tarefa configurada para análise financeira
        """
        return Task(
            description=dedent(f"""
                Realizar análise financeira e de mercado para validar adequação
                dos valores estimados e condições financeiras.
                
                DADOS DE ENTRADA:
                {requisitos_validados}
                
                AÇÕES A EXECUTAR:
                1. Comparar valores estimados com preços de mercado
                2. Analisar adequação das condições de pagamento
                3. Verificar se valores não estão sub ou superestimados
                4. Consultar base de preços de referência
                5. Analisar histórico de fracassos por motivos financeiros
                6. Sugerir ajustes nos valores e condições
                
                RESULTADO ESPERADO:
                JSON com análise de adequação financeira, faixas de valores sugeridas,
                fontes de pesquisa e classificação de risco financeiro.
            """),
            agent=agent,
            expected_output="JSON com análise financeira e sugestões de valores."
        )

    def calcular_risco_task(self, agent, analises_consolidadas):
        """
        Tarefa para calcular risco consolidado.
        Args:
            agent: Agente especialista em riscos
            analises_consolidadas: JSON com todas as análises
        Returns:
            Task: Tarefa configurada para cálculo de risco
        """
        return Task(
            description=dedent(f"""
                Consolidar todas as análises realizadas e calcular o risco geral
                de fracasso da licitação.
                
                ANÁLISES RECEBIDAS:
                {analises_consolidadas}
                
                AÇÕES A EXECUTAR:
                1. Consolidar riscos jurídico, técnico e financeiro
                2. Calcular probabilidade de sucesso baseada no histórico
                3. Identificar fatores críticos de risco
                4. Propor medidas de mitigação específicas
                5. Gerar recomendação final sobre prosseguimento
                6. Definir pontos de monitoramento durante o processo
                
                RESULTADO ESPERADO:
                JSON com risco consolidado, probabilidade de sucesso, fatores de risco,
                medidas de mitigação e recomendação final.
            """),
            agent=agent,
            expected_output="JSON com análise consolidada de risco e recomendações."
        )

    def gerar_edital_task(self, agent, dados_consolidados):
        """
        Tarefa para gerar o conteúdo do edital.
        Args:
            agent: Agente gerador de edital
            dados_consolidados: Todos os dados e análises
        Returns:
            Task: Tarefa configurada para geração do edital
        """
        return Task(
            description=dedent(f"""
                Gerar o conteúdo completo do edital baseado nos requisitos
                validados e nas análises realizadas.
                
                DADOS CONSOLIDADOS:
                {dados_consolidados}
                
                AÇÕES A EXECUTAR:
                1. Selecionar template mais adequado para a categoria
                2. Aplicar os requisitos validados ao template
                3. Incorporar melhorias sugeridas pelas análises
                4. Gerar seções específicas (objeto, habilitação, especificações)
                5. Incluir cláusulas de mitigação de risco identificadas
                6. Formatar conteúdo conforme padrões dos Correios
                
                RESULTADO ESPERADO:
                JSON com conteúdo completo do edital, template utilizado,
                variáveis aplicadas e observações sobre a geração.
            """),
            agent=agent,
            expected_output="JSON com edital completo gerado e metadados."
        )

    def otimizar_edital_task(self, agent, edital_gerado):
        """
        Tarefa para otimizar o edital gerado.
        Args:
            agent: Agente revisor e otimizador
            edital_gerado: Edital gerado na etapa anterior
        Returns:
            Task: Tarefa configurada para otimização
        """
        return Task(
            description=dedent(f"""
                Revisar e otimizar o edital gerado aplicando melhorias finais
                baseadas em boas práticas e lições aprendidas.
                
                EDITAL GERADO:
                {edital_gerado}
                
                AÇÕES A EXECUTAR:
                1. Revisar clareza e completude do texto
                2. Verificar consistência entre seções
                3. Aplicar lições aprendidas do histórico
                4. Incluir cláusulas de sustentabilidade se aplicável
                5. Melhorar formatação e estrutura
                6. Validar conformidade final com normas
                
                RESULTADO ESPERADO:
                JSON com edital otimizado, lista de otimizações aplicadas
                e status final de qualidade.
            """),
            agent=agent,
            expected_output="JSON com edital otimizado e melhorias aplicadas."
        )

    def coordenar_processo_task(self, agent, resultados_completos):
        """
        Tarefa para coordenar e finalizar o processo.
        Args:
            agent: Agente coordenador do processo
            resultados_completos: Todos os resultados das etapas
        Returns:
            Task: Tarefa configurada para coordenação final
        """
        return Task(
            description=dedent(f"""
                Coordenar a finalização do processo de geração do edital,
                consolidar todos os resultados e gerar relatório final.
                
                RESULTADOS COMPLETOS:
                {resultados_completos}
                
                AÇÕES A EXECUTAR:
                1. Consolidar todos os resultados das análises
                2. Validar qualidade final do edital gerado
                3. Gerar relatório executivo com justificativas
                4. Definir status final (aprovado/pendente/rejeitado)
                5. Listar próximos passos recomendados
                6. Documentar lições aprendidas para futuras gerações
                
                RESULTADO ESPERADO:
                JSON com edital final, relatório executivo, status de aprovação,
                recomendações e próximos passos.
            """),
            agent=agent,
            expected_output="JSON com resultado final consolidado e relatório executivo."
        )

    def salvar_edital_task(self, agent, edital_final):
        """
        Tarefa para salvar o edital no banco de dados.
        Args:
            agent: Agente estruturador (reutilizado)
            edital_final: Edital final consolidado
        Returns:
            Task: Tarefa configurada para salvamento
        """
        return Task(
            description=dedent(f"""
                Salvar o edital gerado e todos os dados relacionados no banco de dados
                para controle e histórico.
                
                EDITAL FINAL:
                {edital_final}
                
                AÇÕES A EXECUTAR:
                1. Estruturar dados para salvamento no banco
                2. Gerar ID único para o edital
                3. Salvar requisitos originais e edital gerado
                4. Registrar todas as análises realizadas
                5. Atualizar estatísticas de uso de templates
                6. Criar registro para acompanhamento futuro
                
                RESULTADO ESPERADO:
                Confirmação de salvamento com ID do edital gerado e
                informações para acompanhamento.
            """),
            agent=agent,
            expected_output="Confirmação de salvamento com ID e dados de controle."
        )
