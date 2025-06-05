# Arquivo desativado pois o projeto não utiliza mais LlamaIndex.
# Todo o conteúdo foi comentado para evitar erros de importação.

# from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
# from llama_index.llms.llama_cpp import LlamaCPP
# import os

# # Diretório padrão onde os modelos Llama devem ser armazenados
# MODELS_DIR = os.getenv("LLAMA_MODELS_DIR", "./models/")
# # Diretório padrão onde os dados/documentos para indexação devem ser armazenados
# DATA_DIR = os.getenv("LLAMA_DATA_DIR", "../data/")

# # Função para carregar o modelo Llama local

# def load_llama_llm(model_path=None):
#     """
#     Carrega o modelo Llama local usando LlamaCPP.
#     Args:
#         model_path (str): Caminho para o arquivo do modelo Llama. Se None, usa o padrão em MODELS_DIR.
#     Returns:
#         LlamaCPP: Instância do modelo Llama carregado.
#     """
#     model_path = model_path or os.path.join(MODELS_DIR, "llama-2-7b-chat.ggmlv3.q4_0.bin")
#     llm = LlamaCPP(
#         model_path=model_path,  # Caminho do modelo binário
#         temperature=0.7,        # Temperatura do modelo (criatividade)
#         max_new_tokens=256,     # Máximo de tokens gerados por resposta
#     )
#     return llm

# # Função para indexar documentos de uma pasta

# def build_index_from_dir(data_dir=None, llm=None):
#     """
#     Indexa todos os documentos de uma pasta usando o LlamaIndex.
#     Args:
#         data_dir (str): Caminho para a pasta com documentos (PDF, TXT, DOCX, etc).
#         llm: (opcional) Instância do LLM para customização.
#     Returns:
#         VectorStoreIndex: Índice vetorial criado a partir dos documentos.
#     """
#     data_dir = data_dir or os.path.join(DATA_DIR, "raw_licitacoes/")
#     documents = SimpleDirectoryReader(data_dir).load_data()  # Lê todos os arquivos da pasta
#     index = VectorStoreIndex.from_documents(documents)       # Cria o índice vetorial
#     return index

# # Função para consultar o índice

# def query_index(index, query, llm=None):
#     """
#     Consulta o índice vetorial com um prompt/pergunta.
#     Args:
#         index (VectorStoreIndex): Índice vetorial criado pelo LlamaIndex.
#         query (str): Pergunta ou comando para o modelo responder.
#         llm: (opcional) Instância do LLM para customização.
#     Returns:
#         str: Resposta gerada pelo modelo.
#     """
#     query_engine = index.as_query_engine(llm=llm)  # Cria o mecanismo de consulta
#     response = query_engine.query(query)           # Executa a consulta
#     return response 