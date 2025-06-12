"""
Ferramentas especializadas para geração de editais de licitação.
Cada ferramenta implementa uma funcionalidade específica do processo.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any
from crewai_tools.tools import BaseTool
from api.database import SessionLocal, EditalRequest, EditalGerado, HistoricoEdital, TemplateEdital
from api.edital_models import NivelRisco, CategoriaObjeto, TipoLicitacao
import uuid

# Carregar dados de referência
LEI_14133_PATH = "data/lei_14133_2021.txt"
_LEI_14133_CONTENT = ""
if os.path.exists(LEI_14133_PATH):
    with open(LEI_14133_PATH, 'r', encoding='utf-8') as f:
        _LEI_14133_CONTENT = f.read()

PRECOS_REFERENCIA_PATH = "data/precos_referencia.json"
_PRECOS_REFERENCIA = {}
if os.path.exists(PRECOS_REFERENCIA_PATH):
    with open(PRECOS_REFERENCIA_PATH, 'r', encoding='utf-8') as f:
        _PRECOS_REFERENCIA = json.load(f)

class AnalisarRequisitosTool(BaseTool):
    """
    Ferramenta para analisar e validar requisitos de entrada.
    Verifica completude e consistência dos dados fornecidos.
    """
    name: str = "Analisar Requisitos de Entrada"
    description: str = "Analisa e valida os requisitos fornecidos para geração do edital, identificando lacunas ou inconsistências."
    
    def _run(self, requisitos_json: str) -> str:
        """
        Analisa os requisitos fornecidos.
        Args:
            requisitos_json: JSON com os requisitos da licitação
        Returns:
            Análise dos requisitos com pontos de atenção
        """
        try:
            requisitos = json.loads(requisitos_json)
            
            # Validações básicas
            problemas = []
            sugestoes = []
            
            # Verificar campos obrigatórios
            campos_obrigatorios = ['objeto', 'tipo_licitacao', 'categoria', 'setor_requisitante', 'itens']
            for campo in campos_obrigatorios:
                if not requisitos.get(campo):
                    problemas.append(f"Campo obrigatório '{campo}' não informado")
            
            # Verificar consistência dos itens
            if 'itens' in requisitos and requisitos['itens']:
                for i, item in enumerate(requisitos['itens']):
                    if not item.get('descricao'):
                        problemas.append(f"Item {i+1}: descrição não informada")
                    if not item.get('quantidade') or item['quantidade'] <= 0:
                        problemas.append(f"Item {i+1}: quantidade inválida")
            
            # Verificar valores estimados
            if requisitos.get('valor_total_estimado'):
                if requisitos['valor_total_estimado'] <= 0:
                    problemas.append("Valor total estimado deve ser maior que zero")
            else:
                sugestoes.append("Recomenda-se informar valor total estimado para melhor análise")
            
            # Verificar prazos
            if requisitos.get('prazo_execucao') and requisitos['prazo_execucao'] <= 0:
                problemas.append("Prazo de execução deve ser maior que zero")
            
            if requisitos.get('prazo_proposta') and requisitos['prazo_proposta'] < 5:
                sugestoes.append("Prazo para propostas muito curto, recomenda-se mínimo 5 dias")
            
            # Análise de complexidade
            complexidade = "baixa"
            if len(requisitos.get('requisitos_tecnicos', [])) > 5:
                complexidade = "média"
            if len(requisitos.get('requisitos_tecnicos', [])) > 10:
                complexidade = "alta"
            
            resultado = {
                "status": "aprovado" if not problemas else "pendente",
                "problemas": problemas,
                "sugestoes": sugestoes,
                "complexidade": complexidade,
                "campos_validados": len([c for c in campos_obrigatorios if requisitos.get(c)]),
                "total_campos": len(campos_obrigatorios)
            }
            
            return json.dumps(resultado, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return json.dumps({"erro": f"Erro ao analisar requisitos: {str(e)}"})

class ConsultarHistoricoTool(BaseTool):
    """
    Ferramenta para consultar histórico de editais similares.
    Busca lições aprendidas e padrões de sucesso/fracasso.
    """
    name: str = "Consultar Histórico de Editais"
    description: str = "Consulta histórico de editais similares para identificar padrões de sucesso e fracasso."
    
    def _run(self, categoria: str, objeto: str = "") -> str:
        """
        Consulta histórico de editais similares.
        Args:
            categoria: Categoria do objeto (bens, serviços, etc)
            objeto: Descrição do objeto para busca mais específica
        Returns:
            Histórico relevante com lições aprendidas
        """
        try:
            db = SessionLocal()
            
            # Buscar editais similares
            query = db.query(HistoricoEdital).filter(
                HistoricoEdital.categoria == categoria
            )
            
            if objeto:
                # Busca por palavras-chave no objeto
                palavras = objeto.lower().split()[:3]  # Primeiras 3 palavras
                for palavra in palavras:
                    if len(palavra) > 3:  # Ignorar palavras muito pequenas
                        query = query.filter(HistoricoEdital.objeto.ilike(f"%{palavra}%"))
            
            historico = query.limit(10).all()
            
            if not historico:
                return json.dumps({
                    "encontrados": 0,
                    "mensagem": "Nenhum histórico similar encontrado",
                    "recomendacao": "Proceder com cautela extra devido à falta de histórico"
                })
            
            # Analisar padrões
            sucessos = [h for h in historico if h.sucesso]
            fracassos = [h for h in historico if not h.sucesso]
            
            # Extrair lições aprendidas
            licoes_sucesso = []
            licoes_fracasso = []
            
            for sucesso in sucessos:
                if sucesso.licoes_aprendidas:
                    licoes_sucesso.extend(sucesso.licoes_aprendidas)
            
            for fracasso in fracassos:
                if fracasso.licoes_aprendidas:
                    licoes_fracasso.extend(fracasso.licoes_aprendidas)
                if fracasso.motivo_fracasso:
                    licoes_fracasso.append(f"Evitar: {fracasso.motivo_fracasso}")
            
            # Calcular taxa de sucesso
            taxa_sucesso = len(sucessos) / len(historico) if historico else 0
            
            resultado = {
                "encontrados": len(historico),
                "taxa_sucesso": round(taxa_sucesso * 100, 1),
                "sucessos": len(sucessos),
                "fracassos": len(fracassos),
                "licoes_sucesso": list(set(licoes_sucesso))[:5],  # Top 5 únicas
                "licoes_fracasso": list(set(licoes_fracasso))[:5],  # Top 5 únicas
                "recomendacao": self._gerar_recomendacao(taxa_sucesso, licoes_sucesso, licoes_fracasso)
            }
            
            db.close()
            return json.dumps(resultado, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return json.dumps({"erro": f"Erro ao consultar histórico: {str(e)}"})
    
    def _gerar_recomendacao(self, taxa_sucesso: float, sucessos: List[str], fracassos: List[str]) -> str:
        """Gera recomendação baseada no histórico"""
        if taxa_sucesso >= 0.8:
            return "Categoria com alta taxa de sucesso. Seguir padrões identificados."
        elif taxa_sucesso >= 0.6:
            return "Categoria com taxa moderada de sucesso. Atenção aos fatores de fracasso."
        else:
            return "Categoria com baixa taxa de sucesso. Revisar cuidadosamente os fatores de fracasso."

class ValidarConformidadeTool(BaseTool):
    """
    Ferramenta para validar conformidade jurídica com a Lei 14.133/2021.
    """
    name: str = "Validar Conformidade Jurídica"
    description: str = "Valida conformidade dos requisitos com a Lei 14.133/2021 e outras normas aplicáveis."
    
    def _run(self, requisitos_json: str) -> str:
        """
        Valida conformidade jurídica.
        Args:
            requisitos_json: JSON com requisitos da licitação
        Returns:
            Análise de conformidade jurídica
        """
        try:
            requisitos = json.loads(requisitos_json)
            
            pontos_atencao = []
            sugestoes = []
            conforme = True
            
            # Validar tipo de licitação vs valor
            tipo = requisitos.get('tipo_licitacao')
            valor = requisitos.get('valor_total_estimado', 0)
            categoria = requisitos.get('categoria')
            
            # Regras básicas da Lei 14.133/2021
            if tipo == 'pregao' and categoria not in ['bens', 'servicos']:
                pontos_atencao.append("Pregão só pode ser usado para bens e serviços comuns")
                conforme = False
            
            if tipo == 'concorrencia' and valor < 650000 and categoria in ['bens', 'servicos']:
                sugestoes.append("Para este valor, pregão pode ser mais adequado que concorrência")
            
            # Validar prazos
            prazo_proposta = requisitos.get('prazo_proposta', 0)
            if tipo == 'concorrencia' and prazo_proposta < 30:
                pontos_atencao.append("Concorrência exige prazo mínimo de 30 dias para propostas")
                conforme = False
            elif tipo == 'pregao' and prazo_proposta < 8:
                pontos_atencao.append("Pregão exige prazo mínimo de 8 dias para propostas")
                conforme = False
            
            # Validar requisitos de habilitação
            requisitos_juridicos = requisitos.get('requisitos_juridicos', [])
            tem_regularidade_fiscal = any('fiscal' in req.get('descricao', '').lower() 
                                        for req in requisitos_juridicos)
            if not tem_regularidade_fiscal:
                sugestoes.append("Incluir requisito de regularidade fiscal e trabalhista")
            
            # Validar especificações técnicas
            itens = requisitos.get('itens', [])
            for item in itens:
                specs = item.get('especificacoes_tecnicas', [])
                specs_obrigatorias = [s for s in specs if s.get('obrigatorio', True)]
                if len(specs_obrigatorias) > 10:
                    pontos_atencao.append(f"Item '{item.get('descricao', '')}' tem muitas especificações obrigatórias")
            
            # Calcular risco jurídico
            risco = "baixo"
            if pontos_atencao:
                risco = "alto" if not conforme else "medio"
            
            resultado = {
                "conforme": conforme,
                "risco_juridico": risco,
                "pontos_atencao": pontos_atencao,
                "sugestoes_melhoria": sugestoes,
                "base_legal_aplicavel": [
                    "Lei 14.133/2021 - Lei de Licitações",
                    "Decreto 10.024/2019 - Pregão Eletrônico",
                    "Lei 8.666/1993 - Subsidiária"
                ],
                "observacoes": "Análise baseada na Lei 14.133/2021"
            }
            
            return json.dumps(resultado, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return json.dumps({"erro": f"Erro na validação jurídica: {str(e)}"})

class CalcularRiscoTool(BaseTool):
    """
    Ferramenta para calcular risco consolidado de fracasso.
    """
    name: str = "Calcular Risco de Fracasso"
    description: str = "Calcula risco consolidado baseado em análises jurídica, técnica e financeira."
    
    def _run(self, analises_json: str) -> str:
        """
        Calcula risco consolidado.
        Args:
            analises_json: JSON com todas as análises realizadas
        Returns:
            Análise consolidada de risco
        """
        try:
            analises = json.loads(analises_json)
            
            # Extrair riscos individuais
            risco_juridico = analises.get('analise_juridica', {}).get('risco_juridico', 'medio')
            risco_tecnico = analises.get('analise_tecnica', {}).get('risco_tecnico', 'medio')
            risco_financeiro = analises.get('analise_financeira', {}).get('risco_financeiro', 'medio')
            
            # Converter para valores numéricos
            valores_risco = {
                'baixo': 1,
                'medio': 2,
                'alto': 3,
                'critico': 4
            }
            
            valor_juridico = valores_risco.get(risco_juridico, 2)
            valor_tecnico = valores_risco.get(risco_tecnico, 2)
            valor_financeiro = valores_risco.get(risco_financeiro, 2)
            
            # Calcular risco consolidado (média ponderada)
            # Jurídico tem peso maior
            risco_consolidado = (valor_juridico * 0.4 + valor_tecnico * 0.3 + valor_financeiro * 0.3)
            
            # Converter de volta para categoria
            if risco_consolidado <= 1.5:
                risco_geral = "baixo"
                probabilidade = 0.85
            elif risco_consolidado <= 2.5:
                risco_geral = "medio"
                probabilidade = 0.65
            elif risco_consolidado <= 3.5:
                risco_geral = "alto"
                probabilidade = 0.35
            else:
                risco_geral = "critico"
                probabilidade = 0.15
            
            # Identificar fatores de risco
            fatores_risco = []
            medidas_mitigacao = []
            
            if valor_juridico >= 3:
                fatores_risco.append("Não conformidade jurídica")
                medidas_mitigacao.append("Revisar aspectos jurídicos antes da publicação")
            
            if valor_tecnico >= 3:
                fatores_risco.append("Especificações técnicas inadequadas")
                medidas_mitigacao.append("Simplificar ou ajustar especificações técnicas")
            
            if valor_financeiro >= 3:
                fatores_risco.append("Valores inadequados ao mercado")
                medidas_mitigacao.append("Revisar pesquisa de preços e valores estimados")
            
            # Gerar recomendação
            if risco_geral in ['baixo', 'medio']:
                recomendacao = "Prosseguir com a licitação aplicando as melhorias sugeridas"
            elif risco_geral == 'alto':
                recomendacao = "Revisar pontos críticos antes de prosseguir"
            else:
                recomendacao = "Não recomendado prosseguir sem revisão completa"
            
            resultado = {
                "risco_geral": risco_geral,
                "probabilidade_sucesso": probabilidade,
                "fatores_risco": fatores_risco,
                "medidas_mitigacao": medidas_mitigacao,
                "recomendacao": recomendacao,
                "detalhamento": {
                    "risco_juridico": risco_juridico,
                    "risco_tecnico": risco_tecnico,
                    "risco_financeiro": risco_financeiro,
                    "score_consolidado": round(risco_consolidado, 2)
                }
            }
            
            return json.dumps(resultado, ensure_ascii=False, indent=2)
            
        except Exception as e:
            return json.dumps({"erro": f"Erro no cálculo de risco: {str(e)}"})

class AnalisarMercadoTool(BaseTool):
    """
    Ferramenta para análise de mercado e preços.
    """
    name: str = "Analisar Mercado e Preços"
    description: str = "Analisa adequação dos valores estimados com base em preços de mercado."

    def _run(self, requisitos_json: str) -> str:
        """
        Analisa mercado e preços.
        Args:
            requisitos_json: JSON com requisitos da licitação
        Returns:
            Análise de mercado e sugestões de preços
        """
        try:
            requisitos = json.loads(requisitos_json)

            valor_estimado = requisitos.get('valor_total_estimado', 0)
            itens = requisitos.get('itens', [])

            # Consultar base de preços de referência
            precos_encontrados = []
            for item in itens:
                descricao = item.get('descricao', '').lower()
                for key, value in _PRECOS_REFERENCIA.items():
                    if any(palavra in key.lower() for palavra in descricao.split()[:3]):
                        precos_encontrados.append({
                            "item": item.get('descricao'),
                            "referencia": key,
                            "preco_referencia": value,
                            "quantidade": item.get('quantidade', 1)
                        })

            # Calcular estimativa baseada em referências
            valor_sugerido = 0
            for preco in precos_encontrados:
                valor_sugerido += preco['preco_referencia'] * preco['quantidade']

            # Análise de adequação
            adequado = True
            observacoes = []

            if valor_estimado > 0 and valor_sugerido > 0:
                diferenca_percentual = abs(valor_estimado - valor_sugerido) / valor_sugerido
                if diferenca_percentual > 0.3:  # Mais de 30% de diferença
                    adequado = False
                    observacoes.append(f"Diferença significativa entre valor estimado e referência: {diferenca_percentual:.1%}")

            if not precos_encontrados:
                observacoes.append("Poucos preços de referência encontrados - recomenda-se pesquisa adicional")

            risco_financeiro = "baixo"
            if not adequado:
                risco_financeiro = "alto"
            elif not precos_encontrados:
                risco_financeiro = "medio"

            resultado = {
                "orcamento_adequado": adequado,
                "valor_mercado_min": valor_sugerido * 0.8 if valor_sugerido > 0 else None,
                "valor_mercado_max": valor_sugerido * 1.2 if valor_sugerido > 0 else None,
                "valor_sugerido": valor_sugerido if valor_sugerido > 0 else None,
                "fontes_pesquisa": ["Base interna de preços", "Preços de referência históricos"],
                "risco_financeiro": risco_financeiro,
                "observacoes": "; ".join(observacoes) if observacoes else "Valores dentro da normalidade"
            }

            return json.dumps(resultado, ensure_ascii=False, indent=2)

        except Exception as e:
            return json.dumps({"erro": f"Erro na análise de mercado: {str(e)}"})

class ConsultarTemplatesTool(BaseTool):
    """
    Ferramenta para consultar templates de editais.
    """
    name: str = "Consultar Templates de Editais"
    description: str = "Consulta templates de editais disponíveis por categoria e tipo."

    def _run(self, categoria: str, tipo_licitacao: str) -> str:
        """
        Consulta templates disponíveis.
        Args:
            categoria: Categoria do objeto
            tipo_licitacao: Tipo de licitação
        Returns:
            Template mais adequado
        """
        try:
            db = SessionLocal()

            # Buscar template específico
            template = db.query(TemplateEdital).filter(
                TemplateEdital.categoria == categoria,
                TemplateEdital.tipo_licitacao == tipo_licitacao,
                TemplateEdital.ativo == True
            ).first()

            if not template:
                # Buscar template genérico da categoria
                template = db.query(TemplateEdital).filter(
                    TemplateEdital.categoria == categoria,
                    TemplateEdital.ativo == True
                ).first()

            if not template:
                # Template padrão básico
                resultado = {
                    "template_encontrado": False,
                    "template_id": None,
                    "conteudo": self._template_basico(),
                    "variaveis": ["{{OBJETO}}", "{{VALOR_ESTIMADO}}", "{{PRAZO_EXECUCAO}}"],
                    "observacao": "Usando template básico - recomenda-se criar template específico"
                }
            else:
                resultado = {
                    "template_encontrado": True,
                    "template_id": template.id,
                    "nome": template.nome,
                    "conteudo": template.conteudo_template,
                    "variaveis": template.variaveis or [],
                    "versao": template.versao,
                    "taxa_sucesso": template.taxa_sucesso
                }

            db.close()
            return json.dumps(resultado, ensure_ascii=False, indent=2)

        except Exception as e:
            return json.dumps({"erro": f"Erro ao consultar templates: {str(e)}"})

    def _template_basico(self) -> str:
        """Retorna template básico para casos sem template específico"""
        return """
EDITAL DE LICITAÇÃO Nº {{NUMERO_EDITAL}}

OBJETO: {{OBJETO}}

1. DO OBJETO
{{DESCRICAO_DETALHADA}}

2. DO VALOR ESTIMADO
Valor total estimado: R$ {{VALOR_ESTIMADO}}

3. DOS PRAZOS
Prazo para execução: {{PRAZO_EXECUCAO}} dias
Prazo para propostas: {{PRAZO_PROPOSTA}} dias

4. DA HABILITAÇÃO
{{REQUISITOS_HABILITACAO}}

5. DAS ESPECIFICAÇÕES TÉCNICAS
{{ESPECIFICACOES_TECNICAS}}

6. DAS DISPOSIÇÕES GERAIS
{{DISPOSICOES_GERAIS}}
"""

class GerarEditalTool(BaseTool):
    """
    Ferramenta para gerar o conteúdo final do edital.
    """
    name: str = "Gerar Conteúdo do Edital"
    description: str = "Gera o conteúdo completo do edital baseado nos requisitos e template."

    def _run(self, dados_completos_json: str) -> str:
        """
        Gera conteúdo do edital.
        Args:
            dados_completos_json: JSON com todos os dados necessários
        Returns:
            Conteúdo completo do edital
        """
        try:
            dados = json.loads(dados_completos_json)

            # Extrair dados principais
            requisitos = dados.get('requisitos', {})
            template_info = dados.get('template', {})
            analises = dados.get('analises', {})

            # Usar template ou criar básico
            template = template_info.get('conteudo', self._template_basico())

            # Preparar variáveis para substituição
            variaveis = {
                'NUMERO_EDITAL': f"001/{datetime.now().year}",
                'OBJETO': requisitos.get('objeto', ''),
                'VALOR_ESTIMADO': f"{requisitos.get('valor_total_estimado', 0):,.2f}",
                'PRAZO_EXECUCAO': str(requisitos.get('prazo_execucao', 30)),
                'PRAZO_PROPOSTA': str(requisitos.get('prazo_proposta', 7)),
                'DESCRICAO_DETALHADA': self._gerar_descricao_detalhada(requisitos),
                'REQUISITOS_HABILITACAO': self._gerar_requisitos_habilitacao(requisitos),
                'ESPECIFICACOES_TECNICAS': self._gerar_especificacoes_tecnicas(requisitos),
                'DISPOSICOES_GERAIS': self._gerar_disposicoes_gerais(requisitos, analises)
            }

            # Substituir variáveis no template
            conteudo_final = template
            for var, valor in variaveis.items():
                conteudo_final = conteudo_final.replace(f"{{{{{var}}}}}", valor)

            resultado = {
                "conteudo_edital": conteudo_final,
                "variaveis_utilizadas": list(variaveis.keys()),
                "template_usado": template_info.get('template_id', 'basico'),
                "data_geracao": datetime.now().isoformat(),
                "observacoes": "Edital gerado com base nas análises realizadas"
            }

            return json.dumps(resultado, ensure_ascii=False, indent=2)

        except Exception as e:
            return json.dumps({"erro": f"Erro na geração do edital: {str(e)}"})

    def _gerar_descricao_detalhada(self, requisitos: Dict) -> str:
        """Gera descrição detalhada do objeto"""
        objeto = requisitos.get('objeto', '')
        itens = requisitos.get('itens', [])

        descricao = f"Contratação de {objeto.lower()}.\n\n"
        descricao += "ITENS:\n"

        for i, item in enumerate(itens, 1):
            descricao += f"{i}. {item.get('descricao', '')} - "
            descricao += f"Quantidade: {item.get('quantidade', 0)} {item.get('unidade', 'un')}\n"

        return descricao

    def _gerar_requisitos_habilitacao(self, requisitos: Dict) -> str:
        """Gera seção de requisitos de habilitação"""
        req_juridicos = requisitos.get('requisitos_juridicos', [])

        habilitacao = "Para habilitação, os licitantes deverão apresentar:\n\n"
        habilitacao += "a) Documentação relativa à Habilitação Jurídica;\n"
        habilitacao += "b) Documentação relativa à Qualificação Técnica;\n"
        habilitacao += "c) Documentação relativa à Qualificação Econômico-Financeira;\n"
        habilitacao += "d) Documentação relativa à Regularidade Fiscal e Trabalhista;\n\n"

        if req_juridicos:
            habilitacao += "REQUISITOS ESPECÍFICOS:\n"
            for req in req_juridicos:
                habilitacao += f"- {req.get('descricao', '')}\n"

        return habilitacao

    def _gerar_especificacoes_tecnicas(self, requisitos: Dict) -> str:
        """Gera seção de especificações técnicas"""
        itens = requisitos.get('itens', [])

        especificacoes = "ESPECIFICAÇÕES TÉCNICAS:\n\n"

        for i, item in enumerate(itens, 1):
            especificacoes += f"ITEM {i}: {item.get('descricao', '')}\n"

            specs = item.get('especificacoes_tecnicas', [])
            if specs:
                for spec in specs:
                    tipo = "OBRIGATÓRIO" if spec.get('obrigatorio', True) else "DESEJÁVEL"
                    especificacoes += f"- {spec.get('descricao', '')} ({tipo})\n"

            especificacoes += "\n"

        return especificacoes

    def _gerar_disposicoes_gerais(self, requisitos: Dict, analises: Dict) -> str:
        """Gera disposições gerais baseadas nas análises"""
        disposicoes = "DISPOSIÇÕES GERAIS:\n\n"

        # Adicionar cláusulas baseadas nas análises
        analise_risco = analises.get('analise_risco', {})
        medidas_mitigacao = analise_risco.get('medidas_mitigacao', [])

        if medidas_mitigacao:
            disposicoes += "MEDIDAS DE MITIGAÇÃO DE RISCO:\n"
            for medida in medidas_mitigacao:
                disposicoes += f"- {medida}\n"
            disposicoes += "\n"

        # Cláusulas padrão
        disposicoes += "- A presente licitação reger-se-á pela Lei nº 14.133/2021.\n"
        disposicoes += "- É facultado ao licitante vistoriar o local de execução dos serviços.\n"
        disposicoes += "- Os casos omissos serão resolvidos pela Comissão de Licitação.\n"

        return disposicoes

class OtimizarEditalTool(BaseTool):
    """
    Ferramenta para otimizar o edital gerado.
    """
    name: str = "Otimizar Edital Gerado"
    description: str = "Aplica otimizações finais baseadas em boas práticas e histórico."

    def _run(self, edital_json: str) -> str:
        """
        Otimiza o edital gerado.
        Args:
            edital_json: JSON com o edital gerado
        Returns:
            Edital otimizado
        """
        try:
            dados = json.loads(edital_json)
            conteudo = dados.get('conteudo_edital', '')

            # Aplicar otimizações
            otimizacoes_aplicadas = []

            # 1. Verificar clareza dos prazos
            if 'prazo' in conteudo.lower():
                if 'dias úteis' not in conteudo.lower() and 'dias corridos' not in conteudo.lower():
                    conteudo = conteudo.replace('dias', 'dias corridos')
                    otimizacoes_aplicadas.append("Especificado tipo de dias nos prazos")

            # 2. Adicionar cláusula de sustentabilidade
            if 'sustentabilidade' not in conteudo.lower():
                conteudo += "\n\nCRITÉRIOS DE SUSTENTABILIDADE:\n"
                conteudo += "- Preferência para produtos com certificação ambiental.\n"
                conteudo += "- Observância às práticas de sustentabilidade.\n"
                otimizacoes_aplicadas.append("Adicionados critérios de sustentabilidade")

            # 3. Melhorar formatação
            conteudo = conteudo.replace('\n\n\n', '\n\n')  # Remover linhas extras

            resultado = {
                "conteudo_otimizado": conteudo,
                "otimizacoes_aplicadas": otimizacoes_aplicadas,
                "data_otimizacao": datetime.now().isoformat(),
                "status": "otimizado"
            }

            return json.dumps(resultado, ensure_ascii=False, indent=2)

        except Exception as e:
            return json.dumps({"erro": f"Erro na otimização: {str(e)}"})

    def _template_basico(self) -> str:
        """Template básico reutilizado"""
        return """
EDITAL DE LICITAÇÃO Nº {{NUMERO_EDITAL}}

OBJETO: {{OBJETO}}

1. DO OBJETO
{{DESCRICAO_DETALHADA}}

2. DO VALOR ESTIMADO
Valor total estimado: R$ {{VALOR_ESTIMADO}}

3. DOS PRAZOS
Prazo para execução: {{PRAZO_EXECUCAO}} dias
Prazo para propostas: {{PRAZO_PROPOSTA}} dias

4. DA HABILITAÇÃO
{{REQUISITOS_HABILITACAO}}

5. DAS ESPECIFICAÇÕES TÉCNICAS
{{ESPECIFICACOES_TECNICAS}}

6. DAS DISPOSIÇÕES GERAIS
{{DISPOSICOES_GERAIS}}
"""
