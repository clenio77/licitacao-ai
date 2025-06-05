from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
import os
import time
from datetime import datetime, timedelta
import json
import re # Para extrair IDs de URLs
import uuid

# Caminho para o arquivo que registra licitações já processadas
PROCESSED_LICITACOES_REGISTER = "backend/data/processed_licitacoes_register.json"

def _load_processed_licitacoes():
    """
    Carrega do arquivo JSON os IDs das licitações já processadas.
    Retorno:
        list: Lista de IDs de licitações já processadas.
    """
    if os.path.exists(PROCESSED_LICITACOES_REGISTER):
        with open(PROCESSED_LICITACOES_REGISTER, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError: # Lida com arquivo JSON vazio/corrompido
                return []
    return []

def _save_processed_licitacoes(licitacao_ids: list):
    """
    Salva no arquivo JSON os IDs das licitações processadas.
    Parâmetros:
        licitacao_ids (list): Lista de IDs a serem salvos.
    """
    with open(PROCESSED_LICITACOES_REGISTER, 'w', encoding='utf-8') as f:
        json.dump(licitacao_ids, f, ensure_ascii=False, indent=4)

def _extract_id_from_url(url: str) -> str:
    """
    Extrai um identificador único da URL da licitação (ex: numprp e coduasg).
    Parâmetros:
        url (str): URL da licitação.
    Retorno:
        str: ID extraído ou a própria URL se não encontrar.
    """
    # Regex para pegar o numprp e o coduasg, ou apenas o numprp se disponível
    match_numprp = re.search(r'numprp=(\d+)', url)
    match_coduasg = re.search(r'coduasg=(\d+)', url)

    if match_numprp and match_coduasg:
        return f"{match_coduasg.group(1)}_{match_numprp.group(1)}"
    elif match_numprp:
        return match_numprp.group(1)
    return url # Retorna a URL completa se não encontrar um ID específico

def download_licitacao_edital(url: str, download_path: str = "backend/data/raw_licitacoes"):
    """
    Navega até a URL da licitação e tenta baixar o edital.
    Adaptação para Comprasnet: Procura por links de 'Edital' ou 'Anexos'.
    """
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, args=["--ignore-certificate-errors"])
            context = p.chromium.launch_new_context(ignore_https_errors=True)
            page = browser.new_page()
            page.goto(url, wait_until="domcontentloaded", timeout=60000) # Aumentar timeout

            print(f"Navegando para download: {url}")

            # Tentativa de encontrar o link de download do edital.
            # Comprasnet tem diversas estruturas, isso pode precisar de ajuste fino.
            # Procura por links com texto 'Edital', 'Anexos', ou atributos comuns como 'download'.
            edital_link = page.locator("a:has-text('Edital'), a:has-text('Anexos'), a[download], a.btn-download").first

            if not edital_link.is_visible():
                print("Tentando alternativa: procurar em tabelas ou seções de documentos.")
                # Tenta procurar dentro de elementos que contenham "Documentos"
                edital_link = page.locator("h2:has-text('Documentos') + div a, h3:has-text('Anexos') + div a").first
                if not edital_link.is_visible():
                     # Tenta pegar qualquer link que contenha "edital" ou "anexo" no href
                    edital_link = page.locator("a[href*='edital'], a[href*='anexo']").first

            if edital_link.is_visible():
                print(f"Link do edital encontrado: {edital_link.text_content()}. Tentando baixar...")
                with page.expect_download() as download_info:
                    edital_link.click()
                download = download_info.value
                file_path = os.path.join(download_path, download.suggested_filename)
                download.save_as(file_path)
                print(f"Edital baixado para: {file_path}")
                return file_path
            else:
                print("Link do edital não encontrado na página de detalhes.")
                return None
    except Exception as e:
        print(f"Erro ao baixar edital de {url}: {e}")
        return None
    finally:
        if 'browser' in locals() and browser:
            browser.close()


async def search_new_licitacoes_comprasnet(
    search_url: str = "http://comprasnet.gov.br/acesso.asp?url=/ConsultaLicitacoes/ConsLicitacao_Filtro.asp",
    download_path: str = "backend/data/raw_licitacoes",
    termo_assunto: str = None,
    data_inicial: str = None,
    data_final: str = None,
    modalidade: str = None,
    orgao: str = None,
    valor_min: float = None,
    valor_max: float = None,
    portal: str = None
) -> list:
    """
    Navega no Comprasnet para buscar novos pregões eletrônicos.
    Se termo_assunto, datas ou outros filtros forem fornecidos, tenta preencher os campos do portal.
    Retorna uma lista de dicionários com 'id' e 'url' dos editais encontrados.
    """
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    new_licitacoes_found = []
    processed_licitacao_ids = _load_processed_licitacoes()
    base_portal_url = search_url or "https://www.comprasnet.gov.br/seguro/indexportal.asp"

    # Datas
    if data_inicial:
        start_date_str = data_inicial
    else:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=2)
        start_date_str = start_date.strftime("%d/%m/%Y")
    if data_final:
        end_date_str = data_final
    else:
        end_date = datetime.now()
        end_date_str = end_date.strftime("%d/%m/%Y")

    browser = None
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False, args=["--ignore-certificate-errors"])
            context = await browser.new_context(ignore_https_errors=True)
            page = await browser.new_page()
            await page.goto(base_portal_url, wait_until="domcontentloaded", timeout=60000)
            print(f"Acessando portal Comprasnet: {base_portal_url}")
            try:
                await page.locator("a:has-text('Acesso ao Sistema')").click(timeout=5000)
                await page.wait_for_selector("input#numprp", timeout=10000)
            except Exception:
                print("Não encontrei o link 'Acesso ao Sistema' ou formulário. Tentando outro caminho.")
                search_lic_url = "https://www.comprasnet.gov.br/acesso.asp?url=/ConsultaLicitacoes/ConsLicitacao_Relacao.asp"
                await page.goto(search_lic_url, wait_until="domcontentloaded", timeout=60000)
            print("Preenchendo formulário de busca...")
            await page.locator("#chkModalidade9").check()
            await page.locator("#dt_publicacao_ini").fill(start_date_str)
            await page.locator("#dt_publicacao_fim").fill(end_date_str)
            if termo_assunto:
                try:
                    await page.locator("#objeto").fill(termo_assunto)
                    print(f"Preenchendo campo de objeto/assunto com: {termo_assunto}")
                except Exception:
                    print("Campo de objeto/assunto não encontrado ou não pôde ser preenchido.")
            # Os demais filtros (modalidade, orgao, valor_min, valor_max) podem ser implementados conforme o portal permita
            await page.locator("input[type='submit'][value='Consultar']").click()
            await page.wait_for_selector("table.tabelaResultadosLicitacao", timeout=30000)
            print("Results da busca carregados.")
            rows = page.locator("table.tabelaResultadosLicitacao tr")
            count = await rows.count()
            for i in range(1, count):  # pula o cabeçalho
                row = rows.nth(i)
                tds = row.locator("td")
                # Ajuste o índice abaixo conforme a posição da coluna Órgão (ex: 2 ou 3)
                orgao = await tds.nth(2).inner_text() if await tds.count() > 2 else ""
                link_element = row.locator("a[href*='licitacao_portal_detalhe.asp']")
                url = await link_element.get_attribute('href')
                if url and "licitacao_portal_detalhe.asp" in url and "correios" in orgao.lower():
                    full_url = page.url.split('?')[0].replace("acesso.asp?url=/ConsultaLicitacoes/ConsLicitacao_Relacao.asp", "") + url
                    lic_id = _extract_id_from_url(full_url)
                    if lic_id and lic_id not in processed_licitacao_ids:
                        new_licitacoes_found.append({"id": lic_id, "url": full_url, "orgao": orgao})
                        print(f"Encontrado novo dos Correios: ID={lic_id}, Órgão={orgao}, URL={full_url}")
            print(f"Total de {len(new_licitacoes_found)} novas licitações dos Correios encontradas para processamento.")
            return new_licitacoes_found
    except Exception as e:
        print(f"Erro grave ao buscar licitações no Comprasnet: {e}")
        return []
    finally:
        if browser:
            await browser.close()

async def search_new_licitacoes_correios(
    search_url: str = "https://editais.correios.com.br/app/consultar/licitacoes/index.php",
    download_path: str = "backend/data/raw_licitacoes",
    data_inicial: str = None,
    data_final: str = None,
    **kwargs
) -> list:
    """
    Busca licitações no portal oficial dos Correios, filtrando apenas por data inicial e final.
    Retorna uma lista de dicionários com os dados das licitações encontradas.
    """
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    new_licitacoes_found = []
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False, args=["--ignore-certificate-errors"])
            context = await browser.new_context(ignore_https_errors=True)
            page = await context.new_page()
            await page.goto(search_url, wait_until="domcontentloaded", timeout=60000)

            # Preencher selects obrigatórios
            await page.wait_for_selector('#comboSituacao', timeout=60000)
            await page.select_option('#comboSituacao', label="Publicada - A ser Aberta")
            await page.wait_for_selector('#comboModalidade', timeout=60000)
            await page.select_option('#comboModalidade', label="TODAS")
            await page.wait_for_selector('#comboOrdenacao', timeout=60000)
            await page.select_option('#comboOrdenacao', label="Data de Publicação")

            # Preencher datas se fornecidas
            if data_inicial:
                await page.fill('#dataInicial', data_inicial)
            if data_final:
                await page.fill('#dataFinal', data_final)

            # Espera o carregamento da tabela de resultados ou trata ausência de resultados
            try:
                await page.wait_for_selector('#resultado > div > table tbody tr', timeout=120000)
            except Exception:
                # Verifica se há mensagem de nenhum resultado
                msg = await page.inner_text('#resultado')
                if 'nenhum resultado' in msg.lower():
                    print("Nenhum resultado encontrado para o filtro informado.")
                    return []
                else:
                    raise

            new_licitacoes_found = []
            while True:
                rows = page.locator('#resultado > div > table tbody tr')
                count = await rows.count()
                for i in range(count):
                    row = rows.nth(i)
                    tds = row.locator('td')
                    # Acessa a tabela de detalhes de cada item
                    detalhes_td = tds.nth(1)
                    tabela_detalhes = detalhes_td.locator('table')
                    if await tabela_detalhes.count() == 0:
                        print(f"Linha {i}: tabela de detalhes não encontrada, pulando.")
                        continue
                    trs = tabela_detalhes.locator('tr')
                    # Objeto
                    objeto = await trs.nth(0).locator('td').nth(1).locator('b').inner_text() if await trs.nth(0).locator('td').nth(1).locator('b').count() > 0 else ""
                    # Número Edital
                    numero_edital = await trs.nth(1).locator('td').nth(1).inner_text() if await trs.nth(1).locator('td').nth(1).count() > 0 else ""
                    # Tipo Licitação
                    tipo_licitacao = await trs.nth(1).locator('td').nth(3).inner_text() if await trs.nth(1).locator('td').nth(3).count() > 0 else ""
                    # Data Publicação
                    data_publicacao = await trs.nth(2).locator('td').nth(1).inner_text() if await trs.nth(2).locator('td').nth(1).count() > 0 else ""
                    # Data Abertura
                    data_abertura = await trs.nth(2).locator('td').nth(3).inner_text() if await trs.nth(2).locator('td').nth(3).count() > 0 else ""
                    # Modalidade
                    modalidade = await trs.nth(3).locator('td').nth(1).inner_text() if await trs.nth(3).locator('td').nth(1).count() > 0 else ""
                    # UASG
                    uasg = await trs.nth(3).locator('td').nth(3).inner_text() if await trs.nth(3).locator('td').nth(3).count() > 0 else ""
                    # Dependência
                    dependencia = await trs.nth(4).locator('td').nth(1).inner_text() if await trs.nth(4).locator('td').nth(1).count() > 0 else ""
                    # UF
                    uf = await trs.nth(4).locator('td').nth(3).inner_text() if await trs.nth(4).locator('td').nth(3).count() > 0 else ""
                    # Quantidade Itens
                    quantidade_itens = await trs.nth(5).locator('td').nth(1).inner_text() if await trs.nth(5).locator('td').nth(1).count() > 0 else ""
                    # NUP
                    nup = await trs.nth(5).locator('td').nth(3).inner_text() if await trs.nth(5).locator('td').nth(3).count() > 0 else ""
                    # Link do edital (se houver na lista)
                    url = ""
                    objeto_b = trs.nth(0).locator('td').nth(1).locator('b')
                    if await objeto_b.count() > 0:
                        a_tag = objeto_b.locator('a')
                        if await a_tag.count() > 0:
                            url = await a_tag.first.get_attribute('href')
                    new_licitacoes_found.append({
                        "objeto": objeto,
                        "numero_edital": numero_edital,
                        "tipo_licitacao": tipo_licitacao,
                        "data_publicacao": data_publicacao,
                        "data_abertura": data_abertura,
                        "modalidade": modalidade,
                        "uasg": uasg,
                        "dependencia": dependencia,
                        "uf": uf,
                        "quantidade_itens": quantidade_itens,
                        "nup": nup,
                        "url": url
                    })
                    # Salva no banco de dados
                    try:
                        salvar_licitacao_no_banco({
                            "id": numero_edital or nup or str(i),
                            "objeto": objeto,
                            "data_abertura": data_abertura,
                            "modalidade": modalidade,
                            "link_original": url,
                            "numero_edital": numero_edital,
                            "tipo_licitacao": tipo_licitacao,
                            "data_publicacao": data_publicacao,
                            "uasg": uasg,
                            "dependencia": dependencia,
                            "uf": uf,
                            "quantidade_itens": quantidade_itens,
                            "nup": nup
                        })
                    except Exception as e:
                        print(f"Erro ao salvar licitação no banco: {e}")
                # Verifica se há próxima página
                next_btn = page.locator('a.box-navegacao[title="Próxima Página"]')
                if await next_btn.count() > 0 and await next_btn.is_visible():
                    await next_btn.click()
                    await page.wait_for_selector('#resultado > div > table tbody tr', timeout=120000)
                else:
                    break
            print(f"Total de {len(new_licitacoes_found)} licitações dos Correios encontradas para processamento.")
            return new_licitacoes_found
    except Exception as e:
        print(f"Erro grave ao buscar licitações no portal dos Correios: {e}")
        return []
    finally:
        if 'browser' in locals() and browser:
            await browser.close()

def salvar_licitacao_no_banco(lic):
    from api.database import SessionLocal, Licitacao
    from sqlalchemy.exc import IntegrityError
    db = SessionLocal()
    try:
        licitacao_id = lic.get('id')
        if not licitacao_id:
            print("Licitação sem ID, não será salva.")
            return
        existing = db.query(Licitacao).filter(Licitacao.id == licitacao_id).first()
        if existing:
            print(f"Licitação {licitacao_id} já existe, pulando.")
            return
        nova = Licitacao(
            id=licitacao_id,
            objeto=lic.get('objeto'),
            data_abertura=lic.get('data_abertura'),
            modalidade=lic.get('modalidade'),
            link_original=lic.get('link_original'),
            resumo=lic.get('objeto'),  # ou outro campo, se quiser
            numero_edital=lic.get('numero_edital'),
            tipo_licitacao=lic.get('tipo_licitacao'),
            data_publicacao=lic.get('data_publicacao'),
            uasg=lic.get('uasg'),
            dependencia=lic.get('dependencia'),
            uf=lic.get('uf'),
            quantidade_itens=lic.get('quantidade_itens'),
            nup=lic.get('nup')
        )
        db.add(nova)
        db.commit()
        print(f"Licitação {licitacao_id} salva no banco.")
    except IntegrityError:
        db.rollback()
        print(f"Licitação {licitacao_id} já existe (chave duplicada).")
    except Exception as e:
        db.rollback()
        print(f"Erro ao salvar licitação no banco: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    os.makedirs("backend/data/raw_licitacoes", exist_ok=True)
    os.makedirs("backend/data/", exist_ok=True)

    print("--- Testando a busca de novas licitações ---")
    new_lics = search_new_licitacoes_comprasnet()
    for lic in new_lics:
        print(f"Nova licitação encontrada: ID={lic['id']}, URL={lic['url']}")

    print("\n--- Conteúdo do Registro de Processadas ---")
    print(json.dumps(_load_processed_licitacoes(), indent=4))

    # Após coletar todas as licitações, salvar cada uma no banco
    for lic in new_lics:
        lic_id = lic.get('numero_edital') or str(uuid.uuid4())
        licitacao_dict = {
            "id": lic_id,
            "objeto": lic.get("objeto"),
            "data_abertura": lic.get("data_abertura"),
            "modalidade": lic.get("modalidade"),
            "link_original": lic.get("url"),
            "numero_edital": lic.get("numero_edital"),
            "tipo_licitacao": lic.get("tipo_licitacao"),
            "data_publicacao": lic.get("data_publicacao"),
            "uasg": lic.get("uasg"),
            "dependencia": lic.get("dependencia"),
            "uf": lic.get("uf"),
            "quantidade_itens": lic.get("quantidade_itens"),
            "nup": lic.get("nup")
            # Adicione outros campos conforme o modelo do banco se necessário
        }
        salvar_licitacao_no_banco(licitacao_dict)