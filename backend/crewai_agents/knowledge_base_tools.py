"""
Ferramentas para consultar e utilizar a base de conhecimento de licitações bem-sucedidas.
Integra dados coletados via web scraping com o processo de geração de editais.
"""

import json
import os
from typing import List, Dict, Any, Optional
from crewai_tools.tools import BaseTool
from datetime import datetime
import re
from collections import defaultdict

class KnowledgeBaseTool(BaseTool):
    """
    Ferramenta para consultar base de conhecimento de licitações bem-sucedidas.
    """
    name: str = "Consultar Base de Conhecimento"
    description: str = "Consulta licitações similares bem-sucedidas para extrair boas práticas e padrões de sucesso."
    
    def __init__(self):
        super().__init__()
        self.knowledge_base_path = "data/"
        self.cached_data = None
        self.last_load_time = None
    
    def _run(self, categoria: str, objeto: str = "", tipo_licitacao: str = "") -> str:
        """
        Consulta a base de conhecimento por categoria e objeto.
        
        Args:
            categoria: Categoria da licitação (bens, serviços, obras)
            objeto: Descrição do objeto (opcional)
            tipo_licitacao: Tipo de licitação (opcional)
        
        Returns:
            JSON com licitações similares e insights
        """
        try:
            # Carregar dados da base de conhecimento
            knowledge_data = self._load_knowledge_base()
            
            if not knowledge_data:
                return json.dumps({
                    "encontradas": 0,
                    "mensagem": "Base de conhecimento vazia",
                    "recomendacao": "Execute o scraper para coletar dados"
                })
            
            # Filtrar licitações similares
            similar_licitacoes = self._find_similar_licitacoes(
                knowledge_data, categoria, objeto, tipo_licitacao
            )
            
            if not similar_licitacoes:
                return json.dumps({
                    "encontradas": 0,
                    "mensagem": "Nenhuma licitação similar encontrada",
                    "sugestao": "Usar padrões gerais da categoria"
                })
            
            # Extrair insights e padrões
            insights = self._extract_insights(similar_licitacoes)
            
            # Preparar resposta
            resultado = {
                "encontradas": len(similar_licitacoes),
                "licitacoes_similares": similar_licitacoes[:5],  # Top 5
                "insights": insights,
                "recomendacoes": self._generate_recommendations(insights),
                "data_consulta": datetime.now().isoformat()
            }
            
            return json.dumps(resultado, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return json.dumps({"erro": f"Erro ao consultar base de conhecimento: {str(e)}"})
    
    def _load_knowledge_base(self) -> List[Dict]:
        """Carrega dados da base de conhecimento"""
        # Cache simples para evitar recarregar constantemente
        current_time = datetime.now()
        if (self.cached_data is not None and 
            self.last_load_time is not None and 
            (current_time - self.last_load_time).seconds < 300):  # Cache por 5 minutos
            return self.cached_data
        
        all_data = []
        
        # Procurar arquivos de base de conhecimento
        if os.path.exists(self.knowledge_base_path):
            for filename in os.listdir(self.knowledge_base_path):
                if filename.startswith('knowledge_base_') and filename.endswith('.json'):
                    filepath = os.path.join(self.knowledge_base_path, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            all_data.extend(data)
                    except Exception as e:
                        print(f"Erro ao carregar {filename}: {str(e)}")
        
        # Carregar também dados do histórico existente
        historico_path = os.path.join(self.knowledge_base_path, "historico_editais.json")
        if os.path.exists(historico_path):
            try:
                with open(historico_path, 'r', encoding='utf-8') as f:
                    historico_data = json.load(f)
                    # Converter formato do histórico para formato da base de conhecimento
                    for item in historico_data:
                        if item.get('sucesso', False):
                            converted = self._convert_historico_to_knowledge(item)
                            if converted:
                                all_data.append(converted)
            except Exception as e:
                print(f"Erro ao carregar histórico: {str(e)}")
        
        self.cached_data = all_data
        self.last_load_time = current_time
        return all_data
    
    def _convert_historico_to_knowledge(self, historico_item: Dict) -> Optional[Dict]:
        """Converte item do histórico para formato da base de conhecimento"""
        try:
            return {
                "numero_edital": historico_item.get('id_edital', ''),
                "objeto": historico_item.get('objeto', ''),
                "categoria": historico_item.get('categoria', ''),
                "tipo_licitacao": historico_item.get('tipo_licitacao', ''),
                "modalidade": "eletronica",  # Assumir padrão
                "orgao": "Correios",
                "valor_contratado": historico_item.get('valor_contratado'),
                "numero_propostas": historico_item.get('numero_propostas', 0),
                "data_resultado": historico_item.get('data_resultado', ''),
                "fatores_sucesso": historico_item.get('licoes_aprendidas', []),
                "especificacoes_tecnicas": [],
                "criterio_julgamento": "menor_preco",
                "site_origem": "Histórico Interno"
            }
        except Exception:
            return None
    
    def _find_similar_licitacoes(self, data: List[Dict], categoria: str, objeto: str, tipo_licitacao: str) -> List[Dict]:
        """Encontra licitações similares baseado nos critérios"""
        similar = []
        objeto_words = set(objeto.lower().split()) if objeto else set()
        
        for licitacao in data:
            score = 0
            
            # Pontuação por categoria
            if licitacao.get('categoria', '').lower() == categoria.lower():
                score += 10
            
            # Pontuação por tipo de licitação
            if tipo_licitacao and licitacao.get('tipo_licitacao', '').lower() == tipo_licitacao.lower():
                score += 5
            
            # Pontuação por similaridade do objeto
            if objeto_words:
                licitacao_words = set(licitacao.get('objeto', '').lower().split())
                common_words = objeto_words.intersection(licitacao_words)
                if common_words:
                    score += len(common_words) * 2
            
            # Adicionar se tiver pontuação mínima
            if score >= 5:
                licitacao_copy = licitacao.copy()
                licitacao_copy['similarity_score'] = score
                similar.append(licitacao_copy)
        
        # Ordenar por pontuação de similaridade
        similar.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
        return similar
    
    def _extract_insights(self, licitacoes: List[Dict]) -> Dict[str, Any]:
        """Extrai insights e padrões das licitações similares"""
        if not licitacoes:
            return {}
        
        insights = {
            "total_analisadas": len(licitacoes),
            "fatores_sucesso_comuns": [],
            "especificacoes_frequentes": [],
            "valores_referencia": {},
            "prazos_comuns": {},
            "criterios_julgamento": {},
            "modalidades_preferidas": {},
            "numero_propostas_medio": 0
        }
        
        # Coletar fatores de sucesso
        all_factors = []
        for lic in licitacoes:
            factors = lic.get('fatores_sucesso', [])
            all_factors.extend(factors)
        
        # Contar frequência dos fatores
        factor_count = defaultdict(int)
        for factor in all_factors:
            factor_count[factor] += 1
        
        # Top 5 fatores mais comuns
        insights["fatores_sucesso_comuns"] = [
            {"fator": factor, "frequencia": count}
            for factor, count in sorted(factor_count.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        # Especificações técnicas frequentes
        all_specs = []
        for lic in licitacoes:
            specs = lic.get('especificacoes_tecnicas', [])
            all_specs.extend(specs)
        
        spec_count = defaultdict(int)
        for spec in all_specs:
            spec_count[spec] += 1
        
        insights["especificacoes_frequentes"] = [
            {"especificacao": spec, "frequencia": count}
            for spec, count in sorted(spec_count.items(), key=lambda x: x[1], reverse=True)[:5]
        ]
        
        # Análise de valores
        valores = [lic.get('valor_contratado') or lic.get('valor_estimado') for lic in licitacoes]
        valores = [v for v in valores if v and v > 0]
        
        if valores:
            insights["valores_referencia"] = {
                "minimo": min(valores),
                "maximo": max(valores),
                "medio": sum(valores) / len(valores),
                "mediana": sorted(valores)[len(valores)//2]
            }
        
        # Análise de prazos
        prazos = [lic.get('prazo_execucao') for lic in licitacoes]
        prazos = [p for p in prazos if p and p > 0]
        
        if prazos:
            insights["prazos_comuns"] = {
                "minimo": min(prazos),
                "maximo": max(prazos),
                "medio": sum(prazos) / len(prazos)
            }
        
        # Critérios de julgamento mais usados
        criterios = [lic.get('criterio_julgamento') for lic in licitacoes]
        criterio_count = defaultdict(int)
        for criterio in criterios:
            if criterio:
                criterio_count[criterio] += 1
        
        insights["criterios_julgamento"] = dict(criterio_count)
        
        # Modalidades preferidas
        modalidades = [lic.get('modalidade') for lic in licitacoes]
        modalidade_count = defaultdict(int)
        for modalidade in modalidades:
            if modalidade:
                modalidade_count[modalidade] += 1
        
        insights["modalidades_preferidas"] = dict(modalidade_count)
        
        # Número médio de propostas
        propostas = [lic.get('numero_propostas') for lic in licitacoes]
        propostas = [p for p in propostas if p and p > 0]
        
        if propostas:
            insights["numero_propostas_medio"] = sum(propostas) / len(propostas)
        
        return insights
    
    def _generate_recommendations(self, insights: Dict[str, Any]) -> List[str]:
        """Gera recomendações baseadas nos insights"""
        recommendations = []
        
        # Recomendações baseadas em fatores de sucesso
        fatores_comuns = insights.get("fatores_sucesso_comuns", [])
        if fatores_comuns:
            top_factor = fatores_comuns[0]
            recommendations.append(
                f"Aplicar: {top_factor['fator']} (presente em {top_factor['frequencia']} licitações similares)"
            )
        
        # Recomendações de especificações
        specs_frequentes = insights.get("especificacoes_frequentes", [])
        if specs_frequentes:
            top_spec = specs_frequentes[0]
            recommendations.append(
                f"Considerar especificação: {top_spec['especificacao']} (usada em {top_spec['frequencia']} casos)"
            )
        
        # Recomendações de valores
        valores_ref = insights.get("valores_referencia", {})
        if valores_ref:
            valor_medio = valores_ref.get("medio", 0)
            if valor_medio > 0:
                recommendations.append(
                    f"Valor de referência sugerido: R$ {valor_medio:,.2f} (baseado em licitações similares)"
                )
        
        # Recomendações de prazos
        prazos = insights.get("prazos_comuns", {})
        if prazos:
            prazo_medio = prazos.get("medio", 0)
            if prazo_medio > 0:
                recommendations.append(
                    f"Prazo de execução sugerido: {int(prazo_medio)} dias (baseado em casos similares)"
                )
        
        # Recomendações de modalidade
        modalidades = insights.get("modalidades_preferidas", {})
        if modalidades:
            modalidade_preferida = max(modalidades.items(), key=lambda x: x[1])
            recommendations.append(
                f"Modalidade recomendada: {modalidade_preferida[0]} (usada em {modalidade_preferida[1]} casos)"
            )
        
        # Recomendação sobre competitividade
        num_propostas = insights.get("numero_propostas_medio", 0)
        if num_propostas > 0:
            if num_propostas >= 8:
                recommendations.append("Categoria com boa competitividade - manter especificações atuais")
            elif num_propostas >= 5:
                recommendations.append("Competitividade moderada - considerar flexibilizar especificações")
            else:
                recommendations.append("Baixa competitividade - revisar especificações para ampliar participação")
        
        return recommendations

class ScrapingSchedulerTool(BaseTool):
    """
    Ferramenta para agendar e executar coleta de dados de licitações.
    """
    name: str = "Agendar Coleta de Dados"
    description: str = "Agenda e executa coleta automática de dados de licitações bem-sucedidas."
    
    def _run(self, categorias: str, frequencia: str = "semanal") -> str:
        """
        Agenda coleta de dados para categorias específicas.
        
        Args:
            categorias: Lista de categorias separadas por vírgula
            frequencia: Frequência da coleta (diaria, semanal, mensal)
        
        Returns:
            Status do agendamento
        """
        try:
            categorias_list = [cat.strip() for cat in categorias.split(',')]
            
            # Simular agendamento (em produção, usaria Celery ou similar)
            resultado = {
                "status": "agendado",
                "categorias": categorias_list,
                "frequencia": frequencia,
                "proxima_execucao": self._calculate_next_execution(frequencia),
                "mensagem": f"Coleta agendada para {len(categorias_list)} categorias"
            }
            
            return json.dumps(resultado, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return json.dumps({"erro": f"Erro ao agendar coleta: {str(e)}"})
    
    def _calculate_next_execution(self, frequencia: str) -> str:
        """Calcula próxima execução baseada na frequência"""
        from datetime import timedelta
        
        now = datetime.now()
        
        if frequencia == "diaria":
            next_exec = now + timedelta(days=1)
        elif frequencia == "semanal":
            next_exec = now + timedelta(weeks=1)
        elif frequencia == "mensal":
            next_exec = now + timedelta(days=30)
        else:
            next_exec = now + timedelta(weeks=1)  # Padrão semanal
        
        return next_exec.strftime("%Y-%m-%d %H:%M:%S")

class KnowledgeBaseAnalyticsTool(BaseTool):
    """
    Ferramenta para análise estatística da base de conhecimento.
    """
    name: str = "Analisar Base de Conhecimento"
    description: str = "Gera estatísticas e análises da base de conhecimento de licitações."
    
    def _run(self, tipo_analise: str = "geral") -> str:
        """
        Executa análise da base de conhecimento.
        
        Args:
            tipo_analise: Tipo de análise (geral, categoria, tendencias)
        
        Returns:
            Relatório de análise em JSON
        """
        try:
            kb_tool = KnowledgeBaseTool()
            data = kb_tool._load_knowledge_base()
            
            if not data:
                return json.dumps({
                    "erro": "Base de conhecimento vazia",
                    "sugestao": "Execute o scraper para coletar dados"
                })
            
            if tipo_analise == "geral":
                analise = self._analise_geral(data)
            elif tipo_analise == "categoria":
                analise = self._analise_por_categoria(data)
            elif tipo_analise == "tendencias":
                analise = self._analise_tendencias(data)
            else:
                analise = self._analise_geral(data)
            
            return json.dumps(analise, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return json.dumps({"erro": f"Erro na análise: {str(e)}"})
    
    def _analise_geral(self, data: List[Dict]) -> Dict:
        """Análise geral da base de conhecimento"""
        total = len(data)
        
        # Contagem por categoria
        categorias = defaultdict(int)
        for item in data:
            cat = item.get('categoria', 'indefinida')
            categorias[cat] += 1
        
        # Contagem por tipo de licitação
        tipos = defaultdict(int)
        for item in data:
            tipo = item.get('tipo_licitacao', 'indefinido')
            tipos[tipo] += 1
        
        # Análise de valores
        valores = [item.get('valor_contratado') or item.get('valor_estimado') for item in data]
        valores = [v for v in valores if v and v > 0]
        
        return {
            "total_licitacoes": total,
            "distribuicao_categorias": dict(categorias),
            "distribuicao_tipos": dict(tipos),
            "estatisticas_valores": {
                "total_com_valor": len(valores),
                "valor_minimo": min(valores) if valores else 0,
                "valor_maximo": max(valores) if valores else 0,
                "valor_medio": sum(valores) / len(valores) if valores else 0
            },
            "data_analise": datetime.now().isoformat()
        }
    
    def _analise_por_categoria(self, data: List[Dict]) -> Dict:
        """Análise detalhada por categoria"""
        categorias_data = defaultdict(list)
        
        for item in data:
            cat = item.get('categoria', 'indefinida')
            categorias_data[cat].append(item)
        
        resultado = {}
        
        for categoria, items in categorias_data.items():
            # Análise específica da categoria
            valores = [item.get('valor_contratado') or item.get('valor_estimado') for item in items]
            valores = [v for v in valores if v and v > 0]
            
            propostas = [item.get('numero_propostas') for item in items]
            propostas = [p for p in propostas if p and p > 0]
            
            resultado[categoria] = {
                "total": len(items),
                "valor_medio": sum(valores) / len(valores) if valores else 0,
                "propostas_media": sum(propostas) / len(propostas) if propostas else 0,
                "sites_origem": list(set(item.get('site_origem', '') for item in items))
            }
        
        return resultado
    
    def _analise_tendencias(self, data: List[Dict]) -> Dict:
        """Análise de tendências temporais"""
        # Agrupar por mês/ano
        tendencias = defaultdict(int)
        
        for item in data:
            data_resultado = item.get('data_resultado', '')
            if data_resultado:
                try:
                    # Extrair ano-mês
                    ano_mes = data_resultado[:7]  # YYYY-MM
                    tendencias[ano_mes] += 1
                except:
                    continue
        
        return {
            "tendencias_temporais": dict(sorted(tendencias.items())),
            "periodo_analise": f"{min(tendencias.keys())} a {max(tendencias.keys())}" if tendencias else "N/A",
            "total_periodos": len(tendencias)
        }
