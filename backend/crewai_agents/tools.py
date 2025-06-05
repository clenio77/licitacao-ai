#from crewai_tools import SerperDevTool, FileReadTool, ScrapeWebsiteTool
from web_scraping.mcp_playwright import download_licitacao_edital, search_new_licitacoes_comprasnet
from web_scraping.document_processor import extract_text_from_document
import json
import os
from api.database import SessionLocal, Licitacao
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv
import asyncio # Importar asyncio
from crewai_tools.tools import BaseTool

import requests # Para enviar requisições HTTP

load_dotenv()

# --- Conteúdos de Base de Conhecimento ---
LEI_14133_PATH = "backend/data/lei_14133_2021.txt"
_LEI_14133_CONTENT = ""
if os.path.exists(LEI_14133_PATH):
    with open(LEI_14133_PATH, 'r', encoding='utf-8') as f:
        _LEI_14133_CONTENT = f.read()
else:
    print(f"AVISO: Arquivo da Lei 14.133/2021 não encontrado em {LEI_14133_PATH}. A análise jurídica será limitada.")

PRECOS_REFERENCIA_PATH = "backend/data/precos_referencia.json"
_PRECOS_REFERENCIA = {}
if os.path.exists(PRECOS_REFERENCIA_PATH):
    with open(PRECOS_REFERENCIA_PATH, 'r', encoding='utf-8') as f:
        _PRECOS_REFERENCIA = json.load(f)
else:
    print(f"AVISO: Arquivo de preços de referência '{PRECOS_REFERENCIA_PATH}' não encontrado. A análise de mercado será limitada.")

# --- Configuração da API de Cotação Cambial ---
EXCHANGE_RATE_API_KEY = os.getenv("EXCHANGE_RATE_API_KEY")
EXCHANGE_RATE_BASE_URL = os.getenv("EXCHANGE_RATE_BASE_URL", "[https://v6.exchangerate-api.com/v6](https://v6.exchangerate-api.com/v6)")


class CustomTools:
    @staticmethod
    def buscar_novas_licitacoes(search_url: str = "https://www.comprasnet.gov.br/seguro/indexportal.asp") -> str:
        """
        Busca novas licitações em um portal específico (ex: Comprasnet).
        Retorna uma lista JSON de URLs de licitações encontradas,
        filtrando as que já foram processadas.
        """
        print(f"Agente: Buscando novas licitações em {search_url}...")
        licitacoes = asyncio.run(search_new_licitacoes_comprasnet(search_url=search_url))
        return json.dumps(licitacoes)

    @staticmethod
    def baixar_edital(url: str) -> str:
        """
        Baixa o arquivo do edital de uma URL específica para a pasta de dados brutos.
        Retorna o caminho do arquivo baixado.
        """
        print(f"Agente: Tentando baixar edital de {url}...")
        download_path = "backend/data/raw_licitacoes"
        file_path = download_licitacao_edital(url, download_path)
        if file_path:
            return file_path
        return "Erro ao baixar edital ou link não encontrado."

    @staticmethod
    def extrair_texto_documento(file_path: str) -> str:
        """
        Extrai o conteúdo de texto de um arquivo de edital (PDF/DOCX).
        Retorna o texto limpo do documento.
        """
        print(f"Agente: Extraindo texto de {file_path}...")
        text_content = extract_text_from_document(file_path)
        if text_content:
            return text_content
        return "Não foi possível extrair texto do documento."

    @staticmethod
    def salvar_dados_licitacao(data_json: str) -> str:
        """
        Salva os dados extraídos de uma licitação no banco de dados.
        Atualiza campos de notificação se necessário.
        """
        db = SessionLocal()
        try:
            new_data_dict = json.loads(data_json)
            licitacao_id = new_data_dict.get('id')
            if not licitacao_id: return "Erro: ID da licitação ausente nos dados JSON."
            existing_licitacao = db.query(Licitacao).filter(Licitacao.id == licitacao_id).first()

            if existing_licitacao:
                print(f"Licitação com ID {licitacao_id} já existe. Atualizando...")
                for key, value in new_data_dict.items():
                    if key != 'id' and key != 'data_processamento':
                        if key == 'valor_estimado' and value is not None:
                            try: existing_licitacao.valor_estimado = float(value)
                            except (ValueError, TypeError): existing_licitacao.valor_estimado = None
                        elif key in ['pontos_de_atencao_juridica', 'analise_mercado_texto', 'sugestao_preco_referencia',
                                     'analise_cambial_texto', 'resumo_executivo_gerencial', 'risco_geral', 'recomendacao_final',
                                     'ultima_notificacao_risco', 'ultima_notificacao_variacao_cambial', 'ultima_notificacao_teams_risco']:
                            setattr(existing_licitacao, key, value)
                        else:
                            if hasattr(existing_licitacao, key): setattr(existing_licitacao, key, value)
                            else: print(f"Aviso: Campo '{key}' não encontrado no modelo Licitacao para atualização.")
                existing_licitacao.data_processamento = datetime.now()
                db.commit()
                return f"Dados da licitação com ID {licitacao_id} atualizados com sucesso no DB."
            else:
                print(f"Nova licitação com ID {licitacao_id}. Inserindo...")
                licitacao = Licitacao(
                    id=licitacao_id,
                    objeto=new_data_dict.get('objeto'),
                    data_abertura=new_data_dict.get('data_abertura'),
                    prazo_proposta=new_data_dict.get('prazo_proposta'),
                    valor_estimado=float(new_data_dict['valor_estimado']) if new_data_dict.get('valor_estimado') is not None else None,
                    requisito_habilitacao_principal=new_data_dict.get('requisito_habilitacao_principal'),
                    resumo=new_data_dict.get('resumo'),
                    link_original=new_data_dict.get('link_original'),
                    analise_juridica_texto=new_data_dict.get('analise_juridica_texto'),
                    pontos_de_atencao_juridica=new_data_dict.get('pontos_de_atencao_juridica'),
                    analise_mercado_texto=new_data_dict.get('analise_mercado_texto'),
                    sugestao_preco_referencia=new_data_dict.get('sugestao_preco_referencia'),
                    analise_cambial_texto=new_data_dict.get('analise_cambial_texto'),
                    resumo_executivo_gerencial=new_data_dict.get('resumo_executivo_gerencial'),
                    risco_geral=new_data_dict.get('risco_geral'),
                    recomendacao_final=new_data_dict.get('recomendacao_final')
                )
                db.add(licitacao)
                db.commit()
                db.refresh(licitacao)
                return f"Dados da licitação com ID {licitacao_id} salvos com sucesso no DB."
        except json.JSONDecodeError: db.rollback(); return "Erro: Formato JSON inválido para salvar no DB."
        except Exception as e: db.rollback(); return f"Erro ao salvar/atualizar dados da licitação no DB: {e}"
        finally: db.close()

    @staticmethod
    def consultar_lei_14133(query: str) -> str:
        """
        Consulta o texto da Lei nº 14.133/2021 em busca de informações relevantes.
        Use esta ferramenta para verificar artigos ou princípios da lei.
        """
        if not _LEI_14133_CONTENT: return "Conteúdo da Lei 14.133/2021 não carregado. Verifique o arquivo."
        results = []; query_lower = query.lower()
        for line in _LEI_14133_CONTENT.splitlines():
            if query_lower in line.lower(): results.append(line.strip())
        if results: return "Trechos relevantes da Lei 14.133/2021:\n" + "\n".join(results[:5])
        return "Nenhum trecho relevante encontrado na Lei 14.133/2021 para a sua busca."

    @staticmethod
    def consultar_precos_referencia(item_ou_servico: str) -> str:
        """
        Consulta uma base de dados interna de preços de referência para um item ou serviço.
        Retorna o preço encontrado ou 'Não encontrado'.
        """
        print(f"Agente: Consultando base de preços para '{item_ou_servico}'...")
        for key, value in _PRECOS_REFERENCIA.items():
            if item_ou_servico.lower() in key.lower(): return f"Preço de referência para '{key}': R$ {value:,.2f}"
        return f"Preço de referência para '{item_ou_servico}' não encontrado na base interna."

    @staticmethod
    def pesquisar_preco_web(query: str) -> str:
        """
        Realiza uma pesquisa de preço na web para um determinado item ou serviço.
        (SIMULADO para MVP)
        Retorna uma informação de preço ou "Não foi possível determinar".
        """
        print(f"Agente: Pesquisando preço na web para '{query}' (simulado)...")
        simulated_prices = {
            "notebook": "R$ 3.500,00 (médio)", "servico de ti": "R$ 150,00/hora (estimado)",
            "material de escritorio": "Vários preços dependendo do item. Kit básico R$ 300,00."
        }
        for keyword, price in simulated_prices.items():
            if keyword in query.lower(): return f"Pesquisa web simulada para '{query}': {price}"
        return "Pesquisa web simulada: Não foi possível determinar um preço específico para este item."

    @staticmethod
    def obter_cotacao_cambial(moeda_base: str, moeda_alvo: str) -> str:
        """
        Obtém a cotação atual de uma moeda base em relação a uma moeda alvo.
        Ex: moeda_base='USD', moeda_alvo='BRL'
        Retorna a cotação ou uma mensagem de erro.
        """
        if not EXCHANGE_RATE_API_KEY:
            return "Erro: Chave de API ExchangeRate-API não configurada. Cotação não disponível."

        url = f"{EXCHANGE_RATE_BASE_URL}/{EXCHANGE_RATE_API_KEY}/pair/{moeda_base}/{moeda_alvo}"
        
        try:
            response = requests.get(url)
            response.raise_for_status() # Levanta um erro para status HTTP 4xx/5xx
            data = response.json()

            if data["result"] == "success":
                conversion_rate = data["conversion_rate"]
                return f"Cotação de 1 {moeda_base} para {moeda_alvo}: {conversion_rate:.4f}"
            else:
                return f"Erro na API de cotação cambial: {data.get('error-type', 'Erro desconhecido')}"
        except requests.exceptions.RequestException as e:
            return f"Erro ao conectar à API de cotação cambial: {e}"
        except Exception as e:
            return f"Erro inesperado ao obter cotação cambial: {e}"

    @staticmethod
    def gerar_minuta_documento(titulo: str, conteudo: str, licitacao_id: str) -> str:
        """
        Gera uma minuta de documento em formato de texto para uma licitação específica.
        Retorna o caminho do arquivo gerado.
        """
        document_path = f"backend/data/generated_documents/minuta_{licitacao_id}_{titulo.replace(' ', '_').lower()}.txt"
        os.makedirs(os.path.dirname(document_path), exist_ok=True)
        
        full_content = f"Título: {titulo}\n\nLicitação ID: {licitacao_id}\n\nConteúdo:\n{conteudo}"
        
        try:
            with open(document_path, 'w', encoding='utf-8') as f:
                f.write(full_content)
            print(f"Minuta de documento gerada em: {document_path}")
            return f"Minuta '{titulo}' gerada com sucesso em: {document_path}"
        except Exception as e:
            return f"Erro ao gerar minuta de documento: {e}"
            
    @staticmethod
    def enviar_email_notificacao(destinatario: str, assunto: str, corpo: str) -> str:
        """
        Envia um e-mail de notificação para o destinatário especificado.
        Use para alertar sobre mudanças de cenário, riscos ou eventos importantes.
        """
        sender_address = os.getenv("EMAIL_SENDER_ADDRESS")
        sender_password = os.getenv("EMAIL_SENDER_PASSWORD")
        smtp_server = os.getenv("EMAIL_SMTP_SERVER")
        smtp_port = int(os.getenv("EMAIL_SMTP_PORT", 587))

        if not all([sender_address, sender_password, smtp_server]):
            return "Erro: Configurações de e-mail ausentes no ambiente. Notificação não enviada."

        try:
            msg = MIMEText(corpo, 'html', 'utf-8') # Usar HTML para formatação básica
            msg['From'] = sender_address
            msg['To'] = destinatario
            msg['Subject'] = assunto

            print(f"Agente: Tentando enviar e-mail para {destinatario} com assunto '{assunto}'...")

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()  # Habilita segurança TLS
                server.login(sender_address, sender_password)
                server.send_message(msg)
            print("E-mail de notificação enviado com sucesso!")
            return "E-mail de notificação enviado com sucesso."
        except Exception as e:
            print(f"Erro ao enviar e-mail de notificação: {e}")
            return f"Erro ao enviar e-mail de notificação: {e}"

    @staticmethod
    def enviar_mensagem_teams(assunto: str, corpo: str, licitacao_id: str, link_licitacao: str) -> str:
        """
        Envia uma mensagem de notificação para um canal do Microsoft Teams via Webhook.
        """
        teams_webhook_url = os.getenv("TEAMS_WEBHOOK_URL")

        if not teams_webhook_url:
            return "Erro: URL do Webhook do Teams ausente no ambiente. Notificação não enviada."

        # Estrutura básica de um cartão para Teams (MessageCard)
        message_body = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "FF0000" if "ALTO" in assunto.upper() else ("FFA500" if "MÉDIO" in assunto.upper() else "008000"), # Cor baseada no risco
            "summary": assunto,
            "sections": [
                {
                    "activityTitle": f"**{assunto}**",
                    "activitySubtitle": f"Licitação ID: {licitacao_id}",
                    "activityText": corpo,
                    "markdown": True
                }
            ],
            "potentialAction": [
                {
                    "@type": "OpenUri",
                    "name": "Ver no Dashboard de Licitações",
                    "targets": [
                        { "os": "default", "uri": f"http://localhost:3000/licitacoes/{licitacao_id}" }
                    ]
                },
                {
                    "@type": "OpenUri",
                    "name": "Ver Edital Original",
                    "targets": [
                        { "os": "default", "uri": link_licitacao }
                    ]
                }
            ]
        }

        try:
            response = requests.post(teams_webhook_url, json=message_body)
            response.raise_for_status() # Lança um erro para status HTTP ruins
            print(f"Mensagem enviada para o Teams com sucesso (status: {response.status_code}).")
            return "Mensagem do Teams enviada com sucesso."
        except requests.exceptions.RequestException as e:
            print(f"Erro ao enviar mensagem para o Teams: {e}")
            return f"Erro ao enviar mensagem para o Teams: {e}"

class BuscarNovasLicitacoesTool(BaseTool):
    name: str = "Buscar Novas Licitações no Comprasnet"
    description: str = "Busca novas licitações no portal Comprasnet e retorna uma lista JSON de URLs encontradas."

    def _run(self, search_url: str = "http://comprasnet.gov.br/acesso.asp?url=/ConsultaLicitacoes/ConsLicitacao_Filtro.asp"):
        import asyncio
        import json
        print(f"Agente: Buscando novas licitações em {search_url}...")
        licitacoes = asyncio.run(search_new_licitacoes_comprasnet(search_url=search_url))
        return json.dumps(licitacoes)

# Ferramenta customizada para baixar edital
class BaixarEditalTool(BaseTool):
    name: str = "Baixar Edital"
    description: str = "Baixa o arquivo do edital de uma URL específica para a pasta de dados brutos. Retorna o caminho do arquivo baixado."
    def _run(self, url: str):
        print(f"Agente: Tentando baixar edital de {url}...")
        download_path = "backend/data/raw_licitacoes"
        file_path = download_licitacao_edital(url, download_path)
        if file_path:
            return file_path
        return "Erro ao baixar edital ou link não encontrado."

# Ferramenta customizada para extrair texto de documento
class ExtrairTextoDocumentoTool(BaseTool):
    name: str = "Extrair Texto de Documento"
    description: str = "Extrai o conteúdo de texto de um arquivo de edital (PDF/DOCX). Retorna o texto limpo do documento."
    def _run(self, file_path: str):
        print(f"Agente: Extraindo texto de {file_path}...")
        text_content = extract_text_from_document(file_path)
        if text_content:
            return text_content
        return "Não foi possível extrair texto do documento."

# Ferramenta customizada para salvar dados da licitação
class SalvarDadosLicitacaoTool(BaseTool):
    name: str = "Salvar Dados da Licitação"
    description: str = "Salva os dados extraídos de uma licitação no banco de dados. Atualiza campos de notificação se necessário."
    def _run(self, data_json: str):
        db = SessionLocal()
        try:
            new_data_dict = json.loads(data_json)
            licitacao_id = new_data_dict.get('id')
            if not licitacao_id: return "Erro: ID da licitação ausente nos dados JSON."
            existing_licitacao = db.query(Licitacao).filter(Licitacao.id == licitacao_id).first()
            if existing_licitacao:
                print(f"Licitação com ID {licitacao_id} já existe. Atualizando...")
                for key, value in new_data_dict.items():
                    if key != 'id' and key != 'data_processamento':
                        if key == 'valor_estimado' and value is not None:
                            try: existing_licitacao.valor_estimado = float(value)
                            except (ValueError, TypeError): existing_licitacao.valor_estimado = None
                        elif key in ['pontos_de_atencao_juridica', 'analise_mercado_texto', 'sugestao_preco_referencia',
                                     'analise_cambial_texto', 'resumo_executivo_gerencial', 'risco_geral', 'recomendacao_final',
                                     'ultima_notificacao_risco', 'ultima_notificacao_variacao_cambial', 'ultima_notificacao_teams_risco']:
                            setattr(existing_licitacao, key, value)
                        else:
                            if hasattr(existing_licitacao, key): setattr(existing_licitacao, key, value)
                            else: print(f"Aviso: Campo '{key}' não encontrado no modelo Licitacao para atualização.")
                existing_licitacao.data_processamento = datetime.now()
                db.commit()
                return f"Dados da licitação com ID {licitacao_id} atualizados com sucesso no DB."
            else:
                print(f"Nova licitação com ID {licitacao_id}. Inserindo...")
                licitacao = Licitacao(
                    id=licitacao_id,
                    objeto=new_data_dict.get('objeto'),
                    data_abertura=new_data_dict.get('data_abertura'),
                    prazo_proposta=new_data_dict.get('prazo_proposta'),
                    valor_estimado=float(new_data_dict['valor_estimado']) if new_data_dict.get('valor_estimado') is not None else None,
                    requisito_habilitacao_principal=new_data_dict.get('requisito_habilitacao_principal'),
                    resumo=new_data_dict.get('resumo'),
                    link_original=new_data_dict.get('link_original'),
                    analise_juridica_texto=new_data_dict.get('analise_juridica_texto'),
                    pontos_de_atencao_juridica=new_data_dict.get('pontos_de_atencao_juridica'),
                    analise_mercado_texto=new_data_dict.get('analise_mercado_texto'),
                    sugestao_preco_referencia=new_data_dict.get('sugestao_preco_referencia'),
                    analise_cambial_texto=new_data_dict.get('analise_cambial_texto'),
                    resumo_executivo_gerencial=new_data_dict.get('resumo_executivo_gerencial'),
                    risco_geral=new_data_dict.get('risco_geral'),
                    recomendacao_final=new_data_dict.get('recomendacao_final')
                )
                db.add(licitacao)
                db.commit()
                db.refresh(licitacao)
                return f"Dados da licitação com ID {licitacao_id} salvos com sucesso no DB."
        except json.JSONDecodeError: db.rollback(); return "Erro: Formato JSON inválido para salvar no DB."
        except Exception as e: db.rollback(); return f"Erro ao salvar/atualizar dados da licitação no DB: {e}"
        finally: db.close()

# Ferramenta customizada para consultar Lei 14133/2021
class ConsultarLei14133Tool(BaseTool):
    name: str = "Consultar Lei 14133/2021"
    description: str = "Consulta o texto da Lei nº 14.133/2021 em busca de informações relevantes."
    def _run(self, query: str):
        if not _LEI_14133_CONTENT: return "Conteúdo da Lei 14.133/2021 não carregado. Verifique o arquivo."
        results = []; query_lower = query.lower()
        for line in _LEI_14133_CONTENT.splitlines():
            if query_lower in line.lower(): results.append(line.strip())
        if results: return "Trechos relevantes da Lei 14.133/2021:\n" + "\n".join(results[:5])
        return "Nenhum trecho relevante encontrado na Lei 14.133/2021 para a sua busca."

# Ferramenta customizada para consultar preços de referência
class ConsultarPrecosReferenciaTool(BaseTool):
    name: str = "Consultar Base de Preços de Referência"
    description: str = "Consulta uma base de dados interna de preços de referência para um item ou serviço."
    def _run(self, item_ou_servico: str):
        print(f"Agente: Consultando base de preços para '{item_ou_servico}'...")
        for key, value in _PRECOS_REFERENCIA.items():
            if item_ou_servico.lower() in key.lower(): return f"Preço de referência para '{key}': R$ {value:,.2f}"
        return f"Preço de referência para '{item_ou_servico}' não encontrado na base interna."

# Ferramenta customizada para pesquisar preço na web
class PesquisarPrecoWebTool(BaseTool):
    name: str = "Pesquisar Preço na Web"
    description: str = "Realiza uma pesquisa de preço na web para um determinado item ou serviço. (SIMULADO para MVP)"
    def _run(self, query: str):
        print(f"Agente: Pesquisando preço na web para '{query}' (simulado)...")
        simulated_prices = {
            "notebook": "R$ 3.500,00 (médio)", "servico de ti": "R$ 150,00/hora (estimado)",
            "material de escritorio": "Vários preços dependendo do item. Kit básico R$ 300,00."
        }
        for keyword, price in simulated_prices.items():
            if keyword in query.lower(): return f"Pesquisa web simulada para '{query}': {price}"
        return "Pesquisa web simulada: Não foi possível determinar um preço específico para este item."

# Ferramenta customizada para obter cotação cambial
class ObterCotacaoCambialTool(BaseTool):
    name: str = "Obter Cotação Cambial"
    description: str = "Obtém a cotação atual de uma moeda base em relação a uma moeda alvo."
    def _run(self, moeda_base: str, moeda_alvo: str):
        if not EXCHANGE_RATE_API_KEY:
            return "Erro: Chave de API ExchangeRate-API não configurada. Cotação não disponível."
        url = f"{EXCHANGE_RATE_BASE_URL}/{EXCHANGE_RATE_API_KEY}/pair/{moeda_base}/{moeda_alvo}"
        try:
            response = requests.get(url)
            response.raise_for_status() # Levanta um erro para status HTTP 4xx/5xx
            data = response.json()
            if data["result"] == "success":
                conversion_rate = data["conversion_rate"]
                return f"Cotação de 1 {moeda_base} para {moeda_alvo}: {conversion_rate:.4f}"
            else:
                return f"Erro na API de cotação cambial: {data.get('error-type', 'Erro desconhecido')}"
        except requests.exceptions.RequestException as e:
            return f"Erro ao conectar à API de cotação cambial: {e}"
        except Exception as e:
            return f"Erro inesperado ao obter cotação cambial: {e}"

# Ferramenta customizada para gerar minuta de documento
class GerarMinutaDocumentoTool(BaseTool):
    name: str = "Gerar Minuta de Documento"
    description: str = "Gera uma minuta de documento em formato de texto para uma licitação específica. Retorna o caminho do arquivo gerado."
    def _run(self, titulo: str, conteudo: str, licitacao_id: str):
        document_path = f"backend/data/generated_documents/minuta_{licitacao_id}_{titulo.replace(' ', '_').lower()}.txt"
        os.makedirs(os.path.dirname(document_path), exist_ok=True)
        full_content = f"Título: {titulo}\n\nLicitação ID: {licitacao_id}\n\nConteúdo:\n{conteudo}"
        try:
            with open(document_path, 'w', encoding='utf-8') as f:
                f.write(full_content)
            print(f"Minuta de documento gerada em: {document_path}")
            return f"Minuta '{titulo}' gerada com sucesso em: {document_path}"
        except Exception as e:
            return f"Erro ao gerar minuta de documento: {e}"

# Ferramenta customizada para enviar email de notificação
class EnviarEmailNotificacaoTool(BaseTool):
    name: str = "Enviar Email de Notificação"
    description: str = "Envia um e-mail de notificação para o destinatário especificado."
    def _run(self, destinatario: str, assunto: str, corpo: str):
        sender_address = os.getenv("EMAIL_SENDER_ADDRESS")
        sender_password = os.getenv("EMAIL_SENDER_PASSWORD")
        smtp_server = os.getenv("EMAIL_SMTP_SERVER")
        smtp_port = int(os.getenv("EMAIL_SMTP_PORT", 587))
        if not all([sender_address, sender_password, smtp_server]):
            return "Erro: Configurações de e-mail ausentes no ambiente. Notificação não enviada."
        try:
            msg = MIMEText(corpo, 'html', 'utf-8') # Usar HTML para formatação básica
            msg['From'] = sender_address
            msg['To'] = destinatario
            msg['Subject'] = assunto
            print(f"Agente: Tentando enviar e-mail para {destinatario} com assunto '{assunto}'...")
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()  # Habilita segurança TLS
                server.login(sender_address, sender_password)
                server.send_message(msg)
            print("E-mail de notificação enviado com sucesso!")
            return "E-mail de notificação enviado com sucesso."
        except Exception as e:
            print(f"Erro ao enviar e-mail de notificação: {e}")
            return f"Erro ao enviar e-mail de notificação: {e}"

# Ferramenta customizada para enviar mensagem no Teams
class EnviarMensagemTeamsTool(BaseTool):
    name: str = "Enviar Mensagem Microsoft Teams"
    description: str = "Envia uma mensagem de notificação para um canal do Microsoft Teams via Webhook."
    def _run(self, assunto: str, corpo: str, licitacao_id: str, link_licitacao: str):
        teams_webhook_url = os.getenv("TEAMS_WEBHOOK_URL")
        if not teams_webhook_url:
            return "Erro: URL do Webhook do Teams ausente no ambiente. Notificação não enviada."
        message_body = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "themeColor": "FF0000" if "ALTO" in assunto.upper() else ("FFA500" if "MÉDIO" in assunto.upper() else "008000"),
            "summary": assunto,
            "sections": [
                {
                    "activityTitle": f"**{assunto}**",
                    "activitySubtitle": f"Licitação ID: {licitacao_id}",
                    "activityText": corpo,
                    "markdown": True
                }
            ],
            "potentialAction": [
                {
                    "@type": "OpenUri",
                    "name": "Ver no Dashboard de Licitações",
                    "targets": [
                        { "os": "default", "uri": f"http://localhost:3000/licitacoes/{licitacao_id}" }
                    ]
                },
                {
                    "@type": "OpenUri",
                    "name": "Ver Edital Original",
                    "targets": [
                        { "os": "default", "uri": link_licitacao }
                    ]
                }
            ]
        }
        try:
            response = requests.post(teams_webhook_url, json=message_body)
            response.raise_for_status() # Lança um erro para status HTTP ruins
            print(f"Mensagem enviada para o Teams com sucesso (status: {response.status_code}).")
            return "Mensagem do Teams enviada com sucesso."
        except requests.exceptions.RequestException as e:
            print(f"Erro ao enviar mensagem para o Teams: {e}")
            return f"Erro ao enviar mensagem para o Teams: {e}"