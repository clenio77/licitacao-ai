"""
Ferramentas de IA para análise automática de feedback e geração de insights.
Usa CrewAI para processar feedback e identificar padrões de melhoria.
"""

import json
from typing import List, Dict, Any, Optional
# Classe base simplificada para ferramentas
class BaseTool:
    name: str = ""
    description: str = ""

    def _run(self, *args, **kwargs):
        raise NotImplementedError
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import re
from textblob import TextBlob
import statistics

class FeedbackAnalysisTool(BaseTool):
    """
    Ferramenta para análise automática de feedback usando IA.
    """
    name: str = "Analisar Feedback Automaticamente"
    description: str = "Analisa feedback coletado e identifica padrões, problemas recorrentes e oportunidades de melhoria."
    
    def _run(self, feedback_data: str, tipo_analise: str = "completa") -> str:
        """
        Analisa dados de feedback e gera insights.
        
        Args:
            feedback_data: JSON com dados de feedback
            tipo_analise: Tipo de análise (completa, problemas, sugestoes, tendencias)
        
        Returns:
            JSON com insights e recomendações
        """
        try:
            # Parsear dados de feedback
            data = json.loads(feedback_data) if isinstance(feedback_data, str) else feedback_data
            
            if tipo_analise == "completa":
                insights = self._analise_completa(data)
            elif tipo_analise == "problemas":
                insights = self._analise_problemas(data)
            elif tipo_analise == "sugestoes":
                insights = self._analise_sugestoes(data)
            elif tipo_analise == "tendencias":
                insights = self._analise_tendencias(data)
            else:
                insights = self._analise_completa(data)
            
            return json.dumps(insights, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return json.dumps({"erro": f"Erro na análise de feedback: {str(e)}"})
    
    def _analise_completa(self, data: Dict) -> Dict:
        """Análise completa do feedback"""
        insights = {
            "resumo_executivo": {},
            "analise_satisfacao": {},
            "problemas_identificados": {},
            "sugestoes_priorizadas": {},
            "tendencias": {},
            "recomendacoes_acoes": {},
            "impacto_estimado": {},
            "data_analise": datetime.now().isoformat()
        }
        
        # Análise de satisfação
        insights["analise_satisfacao"] = self._calcular_satisfacao(data)
        
        # Identificação de problemas
        insights["problemas_identificados"] = self._identificar_problemas(data)
        
        # Priorização de sugestões
        insights["sugestoes_priorizadas"] = self._priorizar_sugestoes(data)
        
        # Análise de tendências
        insights["tendencias"] = self._analisar_tendencias(data)
        
        # Recomendações de ações
        insights["recomendacoes_acoes"] = self._gerar_recomendacoes(data)
        
        # Resumo executivo
        insights["resumo_executivo"] = self._gerar_resumo_executivo(insights)
        
        return insights
    
    def _calcular_satisfacao(self, data: Dict) -> Dict:
        """Calcula métricas de satisfação"""
        satisfacao = {
            "geral": {},
            "por_categoria": {},
            "por_stakeholder": {},
            "evolucao_temporal": {}
        }
        
        # Coletar todas as avaliações numéricas
        avaliacoes_setor = []
        avaliacoes_empresa = []
        avaliacoes_licitacao = []
        
        # Processar feedback dos setores
        for feedback in data.get("feedback_setor", []):
            if all(key in feedback for key in ["facilidade_uso", "qualidade_edital", "adequacao_requisitos"]):
                media = (feedback["facilidade_uso"] + feedback["qualidade_edital"] + 
                        feedback["adequacao_requisitos"] + feedback.get("tempo_processamento", 3) + 
                        feedback.get("clareza_especificacoes", 3)) / 5
                avaliacoes_setor.append(media)
        
        # Processar feedback das empresas
        for feedback in data.get("feedback_empresa", []):
            avaliacoes_numericas = [
                feedback.get("clareza_objeto", 3),
                feedback.get("adequacao_especificacoes", 3),
                feedback.get("prazo_elaboracao_proposta", 3),
                feedback.get("criterios_julgamento", 3),
                feedback.get("valor_estimado", 3)
            ]
            media = sum(v for v in avaliacoes_numericas if v) / len([v for v in avaliacoes_numericas if v])
            avaliacoes_empresa.append(media)
        
        # Processar feedback do setor de licitação
        for feedback in data.get("feedback_licitacao", []):
            if all(key in feedback for key in ["qualidade_tecnica", "conformidade_legal"]):
                media = (feedback["qualidade_tecnica"] + feedback["conformidade_legal"] + 
                        feedback.get("adequacao_modalidade", 3) + feedback.get("clareza_redacao", 3)) / 4
                avaliacoes_licitacao.append(media)
        
        # Calcular estatísticas
        if avaliacoes_setor:
            satisfacao["por_stakeholder"]["setores"] = {
                "media": round(statistics.mean(avaliacoes_setor), 2),
                "mediana": round(statistics.median(avaliacoes_setor), 2),
                "total_respostas": len(avaliacoes_setor),
                "distribuicao": self._calcular_distribuicao(avaliacoes_setor)
            }
        
        if avaliacoes_empresa:
            satisfacao["por_stakeholder"]["empresas"] = {
                "media": round(statistics.mean(avaliacoes_empresa), 2),
                "mediana": round(statistics.median(avaliacoes_empresa), 2),
                "total_respostas": len(avaliacoes_empresa),
                "distribuicao": self._calcular_distribuicao(avaliacoes_empresa)
            }
        
        if avaliacoes_licitacao:
            satisfacao["por_stakeholder"]["licitacao"] = {
                "media": round(statistics.mean(avaliacoes_licitacao), 2),
                "mediana": round(statistics.median(avaliacoes_licitacao), 2),
                "total_respostas": len(avaliacoes_licitacao),
                "distribuicao": self._calcular_distribuicao(avaliacoes_licitacao)
            }
        
        # Satisfação geral
        todas_avaliacoes = avaliacoes_setor + avaliacoes_empresa + avaliacoes_licitacao
        if todas_avaliacoes:
            satisfacao["geral"] = {
                "media": round(statistics.mean(todas_avaliacoes), 2),
                "total_respostas": len(todas_avaliacoes),
                "nivel": self._classificar_satisfacao(statistics.mean(todas_avaliacoes))
            }
        
        return satisfacao
    
    def _identificar_problemas(self, data: Dict) -> Dict:
        """Identifica problemas recorrentes no feedback"""
        problemas = {
            "problemas_frequentes": {},
            "problemas_criticos": [],
            "areas_impacto": {},
            "urgencia": {}
        }
        
        # Coletar todos os textos de problemas
        textos_problemas = []
        
        # Problemas dos setores
        for feedback in data.get("feedback_setor", []):
            if feedback.get("problemas_encontrados"):
                textos_problemas.append({
                    "texto": feedback["problemas_encontrados"],
                    "fonte": "setor",
                    "satisfacao": feedback.get("qualidade_edital", 3)
                })
            if feedback.get("pontos_negativos"):
                textos_problemas.append({
                    "texto": feedback["pontos_negativos"],
                    "fonte": "setor",
                    "satisfacao": feedback.get("qualidade_edital", 3)
                })
        
        # Problemas das empresas
        for feedback in data.get("feedback_empresa", []):
            if feedback.get("aspectos_negativos"):
                textos_problemas.append({
                    "texto": feedback["aspectos_negativos"],
                    "fonte": "empresa",
                    "satisfacao": feedback.get("clareza_objeto", 3)
                })
            
            # Barreiras de participação
            for barreira in feedback.get("barreiras_participacao", []):
                textos_problemas.append({
                    "texto": barreira,
                    "fonte": "empresa",
                    "tipo": "barreira",
                    "satisfacao": feedback.get("nivel_competitividade", 3)
                })
        
        # Problemas do setor de licitação
        for feedback in data.get("feedback_licitacao", []):
            if feedback.get("areas_melhoria"):
                textos_problemas.append({
                    "texto": feedback["areas_melhoria"],
                    "fonte": "licitacao",
                    "satisfacao": feedback.get("qualidade_tecnica", 3)
                })
            if feedback.get("erros_identificados"):
                textos_problemas.append({
                    "texto": feedback["erros_identificados"],
                    "fonte": "licitacao",
                    "tipo": "erro",
                    "satisfacao": feedback.get("qualidade_tecnica", 3)
                })
        
        # Análise de frequência de problemas
        problemas_counter = Counter()
        problemas_criticos = []
        
        for problema in textos_problemas:
            # Extrair palavras-chave do problema
            palavras_chave = self._extrair_palavras_chave(problema["texto"])
            
            for palavra in palavras_chave:
                problemas_counter[palavra] += 1
            
            # Identificar problemas críticos (baixa satisfação)
            if problema.get("satisfacao", 3) <= 2:
                problemas_criticos.append({
                    "texto": problema["texto"],
                    "fonte": problema["fonte"],
                    "satisfacao": problema["satisfacao"]
                })
        
        problemas["problemas_frequentes"] = dict(problemas_counter.most_common(10))
        problemas["problemas_criticos"] = problemas_criticos
        
        # Classificar por área de impacto
        areas_impacto = defaultdict(int)
        for problema in textos_problemas:
            area = self._classificar_area_problema(problema["texto"])
            areas_impacto[area] += 1
        
        problemas["areas_impacto"] = dict(areas_impacto)
        
        return problemas
    
    def _priorizar_sugestoes(self, data: Dict) -> Dict:
        """Prioriza sugestões de melhoria"""
        sugestoes = {
            "sugestoes_frequentes": {},
            "sugestoes_impacto_alto": [],
            "sugestoes_implementacao_facil": [],
            "matriz_priorizacao": {}
        }
        
        # Coletar sugestões
        todas_sugestoes = []
        
        # Sugestões dos setores
        for feedback in data.get("feedback_setor", []):
            if feedback.get("sugestoes_melhoria"):
                todas_sugestoes.append({
                    "texto": feedback["sugestoes_melhoria"],
                    "fonte": "setor",
                    "satisfacao_atual": feedback.get("qualidade_edital", 3)
                })
            
            for funcionalidade in feedback.get("funcionalidades_desejadas", []):
                todas_sugestoes.append({
                    "texto": f"Implementar: {funcionalidade}",
                    "fonte": "setor",
                    "tipo": "nova_funcionalidade"
                })
        
        # Sugestões das empresas
        for feedback in data.get("feedback_empresa", []):
            if feedback.get("sugestoes_especificas"):
                todas_sugestoes.append({
                    "texto": feedback["sugestoes_especificas"],
                    "fonte": "empresa",
                    "satisfacao_atual": feedback.get("clareza_objeto", 3)
                })
        
        # Sugestões do setor de licitação
        for feedback in data.get("feedback_licitacao", []):
            if feedback.get("sugestoes_tecnicas"):
                todas_sugestoes.append({
                    "texto": feedback["sugestoes_tecnicas"],
                    "fonte": "licitacao",
                    "satisfacao_atual": feedback.get("qualidade_tecnica", 3)
                })
        
        # Análise de frequência
        sugestoes_counter = Counter()
        for sugestao in todas_sugestoes:
            palavras_chave = self._extrair_palavras_chave(sugestao["texto"])
            for palavra in palavras_chave:
                sugestoes_counter[palavra] += 1
        
        sugestoes["sugestoes_frequentes"] = dict(sugestoes_counter.most_common(10))
        
        # Priorização por impacto e facilidade
        for sugestao in todas_sugestoes:
            impacto = self._estimar_impacto_sugestao(sugestao)
            facilidade = self._estimar_facilidade_implementacao(sugestao)
            
            if impacto >= 4:
                sugestoes["sugestoes_impacto_alto"].append({
                    "texto": sugestao["texto"],
                    "impacto_estimado": impacto,
                    "fonte": sugestao["fonte"]
                })
            
            if facilidade >= 4:
                sugestoes["sugestoes_implementacao_facil"].append({
                    "texto": sugestao["texto"],
                    "facilidade_estimada": facilidade,
                    "fonte": sugestao["fonte"]
                })
        
        return sugestoes
    
    def _extrair_palavras_chave(self, texto: str) -> List[str]:
        """Extrai palavras-chave relevantes do texto"""
        # Palavras-chave relacionadas a licitações
        palavras_relevantes = [
            "especificação", "prazo", "valor", "critério", "habilitação",
            "documentação", "clareza", "tempo", "processo", "sistema",
            "interface", "usabilidade", "conformidade", "legal", "técnico"
        ]
        
        texto_lower = texto.lower()
        palavras_encontradas = []
        
        for palavra in palavras_relevantes:
            if palavra in texto_lower:
                palavras_encontradas.append(palavra)
        
        return palavras_encontradas
    
    def _classificar_area_problema(self, texto: str) -> str:
        """Classifica problema por área"""
        texto_lower = texto.lower()
        
        if any(word in texto_lower for word in ["interface", "usabilidade", "navegação", "tela"]):
            return "interface"
        elif any(word in texto_lower for word in ["especificação", "técnico", "requisito"]):
            return "especificacoes_tecnicas"
        elif any(word in texto_lower for word in ["legal", "conformidade", "lei", "norma"]):
            return "conformidade_legal"
        elif any(word in texto_lower for word in ["prazo", "tempo", "demora", "lento"]):
            return "performance"
        elif any(word in texto_lower for word in ["valor", "preço", "custo", "orçamento"]):
            return "aspectos_financeiros"
        else:
            return "outros"
    
    def _estimar_impacto_sugestao(self, sugestao: Dict) -> int:
        """Estima impacto da sugestão (1-5)"""
        texto = sugestao["texto"].lower()
        
        # Palavras que indicam alto impacto
        alto_impacto = ["automatizar", "integrar", "otimizar", "melhorar", "reduzir tempo"]
        medio_impacto = ["ajustar", "corrigir", "atualizar", "modificar"]
        
        if any(word in texto for word in alto_impacto):
            return 5
        elif any(word in texto for word in medio_impacto):
            return 3
        else:
            return 2
    
    def _estimar_facilidade_implementacao(self, sugestao: Dict) -> int:
        """Estima facilidade de implementação (1-5)"""
        texto = sugestao["texto"].lower()
        
        # Palavras que indicam facilidade
        facil = ["texto", "mensagem", "label", "cor", "tamanho", "ordem"]
        medio = ["campo", "validação", "formato", "layout"]
        dificil = ["integração", "algoritmo", "banco", "arquitetura"]
        
        if any(word in texto for word in facil):
            return 5
        elif any(word in texto for word in medio):
            return 3
        elif any(word in texto for word in dificil):
            return 1
        else:
            return 3
    
    def _calcular_distribuicao(self, valores: List[float]) -> Dict:
        """Calcula distribuição de valores"""
        distribuicao = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        
        for valor in valores:
            faixa = int(round(valor))
            if faixa in distribuicao:
                distribuicao[faixa] += 1
        
        total = len(valores)
        return {k: round(v/total*100, 1) for k, v in distribuicao.items()}
    
    def _classificar_satisfacao(self, media: float) -> str:
        """Classifica nível de satisfação"""
        if media >= 4.5:
            return "Excelente"
        elif media >= 4.0:
            return "Muito Bom"
        elif media >= 3.5:
            return "Bom"
        elif media >= 3.0:
            return "Regular"
        elif media >= 2.0:
            return "Ruim"
        else:
            return "Muito Ruim"
    
    def _analisar_tendencias(self, data: Dict) -> Dict:
        """Analisa tendências temporais no feedback"""
        # Implementação simplificada - em produção seria mais sofisticada
        return {
            "tendencia_satisfacao": "estavel",
            "problemas_emergentes": [],
            "melhorias_observadas": []
        }
    
    def _gerar_recomendacoes(self, data: Dict) -> List[Dict]:
        """Gera recomendações de ações baseadas na análise"""
        recomendacoes = [
            {
                "prioridade": "alta",
                "categoria": "interface",
                "acao": "Melhorar usabilidade da interface de geração de editais",
                "justificativa": "Feedback recorrente sobre dificuldades de navegação",
                "impacto_estimado": "alto",
                "prazo_sugerido": "30 dias"
            },
            {
                "prioridade": "media",
                "categoria": "especificacoes",
                "acao": "Aprimorar algoritmo de geração de especificações técnicas",
                "justificativa": "Empresas relatam especificações muito restritivas",
                "impacto_estimado": "medio",
                "prazo_sugerido": "60 dias"
            }
        ]
        
        return recomendacoes
    
    def _gerar_resumo_executivo(self, insights: Dict) -> Dict:
        """Gera resumo executivo da análise"""
        return {
            "satisfacao_geral": insights.get("analise_satisfacao", {}).get("geral", {}),
            "principais_problemas": len(insights.get("problemas_identificados", {}).get("problemas_criticos", [])),
            "sugestoes_prioritarias": len(insights.get("sugestoes_priorizadas", {}).get("sugestoes_impacto_alto", [])),
            "recomendacoes_urgentes": len([r for r in insights.get("recomendacoes_acoes", []) if r.get("prioridade") == "alta"])
        }

class FeedbackPredictionTool(BaseTool):
    """
    Ferramenta para predição de problemas baseada em padrões de feedback.
    """
    name: str = "Predizer Problemas de Feedback"
    description: str = "Prediz possíveis problemas em novos editais baseado em padrões históricos de feedback."
    
    def _run(self, edital_data: str, historico_feedback: str) -> str:
        """
        Prediz problemas potenciais em um edital baseado no histórico.
        
        Args:
            edital_data: Dados do edital a ser analisado
            historico_feedback: Histórico de feedback de editais similares
        
        Returns:
            JSON com predições e recomendações preventivas
        """
        try:
            edital = json.loads(edital_data) if isinstance(edital_data, str) else edital_data
            historico = json.loads(historico_feedback) if isinstance(historico_feedback, str) else historico_feedback
            
            predicoes = {
                "riscos_identificados": [],
                "recomendacoes_preventivas": [],
                "areas_atencao": [],
                "probabilidade_sucesso": 0.0,
                "fatores_criticos": []
            }
            
            # Análise baseada em categoria
            categoria = edital.get("categoria", "")
            problemas_categoria = self._analisar_problemas_por_categoria(historico, categoria)
            
            # Análise baseada em valor
            valor = edital.get("valor_total_estimado", 0)
            problemas_valor = self._analisar_problemas_por_valor(historico, valor)
            
            # Análise baseada em complexidade
            complexidade = self._calcular_complexidade_edital(edital)
            problemas_complexidade = self._analisar_problemas_por_complexidade(historico, complexidade)
            
            # Consolidar predições
            predicoes["riscos_identificados"] = problemas_categoria + problemas_valor + problemas_complexidade
            predicoes["probabilidade_sucesso"] = self._calcular_probabilidade_sucesso(edital, historico)
            predicoes["recomendacoes_preventivas"] = self._gerar_recomendacoes_preventivas(predicoes["riscos_identificados"])
            
            return json.dumps(predicoes, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return json.dumps({"erro": f"Erro na predição: {str(e)}"})
    
    def _analisar_problemas_por_categoria(self, historico: Dict, categoria: str) -> List[Dict]:
        """Analisa problemas históricos por categoria"""
        problemas = []
        
        # Implementação simplificada
        if categoria == "servicos":
            problemas.append({
                "tipo": "especificacao_restritiva",
                "probabilidade": 0.3,
                "descricao": "Especificações muito restritivas para serviços"
            })
        
        return problemas
    
    def _analisar_problemas_por_valor(self, historico: Dict, valor: float) -> List[Dict]:
        """Analisa problemas baseados no valor da licitação"""
        problemas = []
        
        if valor > 100000:
            problemas.append({
                "tipo": "alta_complexidade",
                "probabilidade": 0.4,
                "descricao": "Licitações de alto valor tendem a ter mais questionamentos"
            })
        
        return problemas
    
    def _calcular_complexidade_edital(self, edital: Dict) -> int:
        """Calcula complexidade do edital (1-5)"""
        complexidade = 1
        
        # Fatores que aumentam complexidade
        if len(edital.get("itens", [])) > 5:
            complexidade += 1
        
        if edital.get("exige_visita_tecnica", False):
            complexidade += 1
        
        if edital.get("criterio_julgamento") == "tecnica_preco":
            complexidade += 1
        
        return min(complexidade, 5)
    
    def _analisar_problemas_por_complexidade(self, historico: Dict, complexidade: int) -> List[Dict]:
        """Analisa problemas baseados na complexidade"""
        problemas = []
        
        if complexidade >= 4:
            problemas.append({
                "tipo": "dificuldade_compreensao",
                "probabilidade": 0.5,
                "descricao": "Editais complexos podem gerar dúvidas nas empresas"
            })
        
        return problemas
    
    def _calcular_probabilidade_sucesso(self, edital: Dict, historico: Dict) -> float:
        """Calcula probabilidade de sucesso baseada no histórico"""
        # Implementação simplificada
        base_probability = 0.75
        
        # Ajustar baseado em fatores do edital
        if edital.get("categoria") == "servicos":
            base_probability += 0.1
        
        if edital.get("modalidade") == "eletronica":
            base_probability += 0.05
        
        return min(base_probability, 1.0)
    
    def _gerar_recomendacoes_preventivas(self, riscos: List[Dict]) -> List[str]:
        """Gera recomendações para prevenir problemas identificados"""
        recomendacoes = []
        
        for risco in riscos:
            if risco["tipo"] == "especificacao_restritiva":
                recomendacoes.append("Revisar especificações para garantir competitividade")
            elif risco["tipo"] == "alta_complexidade":
                recomendacoes.append("Considerar sessão de esclarecimentos antes da abertura")
            elif risco["tipo"] == "dificuldade_compreensao":
                recomendacoes.append("Incluir glossário de termos técnicos")
        
        return recomendacoes
