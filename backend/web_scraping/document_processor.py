import pypdf
from docx import Document
import os

def extract_text_from_document(file_path: str) -> str:
    """
    Extrai texto de arquivos PDF ou DOCX.
    Parâmetros:
        file_path (str): Caminho do arquivo a ser processado.
    Retorno:
        str: Texto extraído do documento ou string vazia em caso de erro.
    Observação:
        - Para arquivos .doc, recomenda-se converter para .docx ou .pdf antes de usar.
    """
    text_content = ""
    if not os.path.exists(file_path):
        print(f"Erro: Arquivo não encontrado em {file_path}")
        return ""

    try:
        if file_path.lower().endswith(".pdf"):
            with open(file_path, 'rb') as file:
                reader = pypdf.PdfReader(file)
                for page in reader.pages:
                    text_content += page.extract_text() or ""
        elif file_path.lower().endswith((".docx")):
            doc = Document(file_path)
            for paragraph in doc.paragraphs:
                text_content += paragraph.text + "\n"
        elif file_path.lower().endswith((".doc")):
            # .doc files are harder. For MVP, we'll suggest converting to .docx or PDF.
            # Você pode usar uma biblioteca como textract para suporte robusto a .doc.
            print(f"AVISO: Arquivo .doc ({file_path}) não é suportado diretamente neste MVP. Por favor, converta para .pdf ou .docx.")
            return ""
        else:
            print(f"Formato de arquivo não suportado para extração de texto: {file_path}")
            return ""

        print(f"Texto extraído de: {file_path[:50]}...")
        return text_content
    except Exception as e:
        print(f"Erro ao extrair texto do documento {file_path}: {e}")
        return ""

if __name__ == "__main__":
    # Exemplo de uso (requer um PDF ou DOCX de teste em backend/data/raw_licitacoes)
    # Crie um arquivo de teste para testar:
    # Por exemplo: backend/data/raw_licitacoes/edital_exemplo_mvp.pdf
    sample_pdf_path = "backend/data/raw_licitacoes/edital_exemplo_mvp.pdf"
    if os.path.exists(sample_pdf_path):
        extracted_text = extract_text_from_document(sample_pdf_path)
        if extracted_text:
            print("\n--- Texto Extraído (Primeiras 500 chars) ---")
            print(extracted_text[:500])
    else:
        print(f"Crie um arquivo de teste, ex: {sample_pdf_path}, para testar a extração de texto.")