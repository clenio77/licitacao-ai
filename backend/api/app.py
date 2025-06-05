from fastapi import FastAPI, Depends, HTTPException, Body, Path, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import os
from datetime import datetime
from api.database import SessionLocal, Licitacao, create_db_tables, get_db
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from web_scraping.mcp_playwright import search_new_licitacoes_correios
import openai
from dotenv import load_dotenv

load_dotenv()

# Modelos Pydantic para validação e documentação da API
class LicitacaoBase(BaseModel):
    """
    Modelo base para licitações, usado para entrada e saída de dados na API.
    Cada campo representa uma informação relevante de uma licitação.
    """
    id: str
    objeto: str
    data_abertura: Optional[str] = None
    prazo_proposta: Optional[str] = None
    valor_estimado: Optional[float] = None
    requisito_habilitacao_principal: Optional[str] = None
    resumo: Optional[str] = None
    link_original: Optional[str] = None
    status: Optional[str] = "processado_mvp"
    analise_juridica_texto: Optional[str] = None
    pontos_de_atencao_juridica: Optional[List[str]] = None
    analise_mercado_texto: Optional[str] = None
    sugestao_preco_referencia: Optional[float] = None
    analise_cambial_texto: Optional[str] = None
    resumo_executivo_gerencial: Optional[str] = None
    risco_geral: Optional[str] = None
    recomendacao_final: Optional[str] = None
    ultima_notificacao_risco: Optional[datetime] = None
    ultima_notificacao_variacao_cambial: Optional[datetime] = None
    ultima_notificacao_teams_risco: Optional[datetime] = None

    class Config:
        from_attributes = True # Permite conversão ORM -> Pydantic

class LicitacaoCreate(LicitacaoBase):
    """Modelo para criação de nova licitação."""
    pass

class LicitacaoResponse(LicitacaoBase):
    """Modelo de resposta para endpoints que retornam licitações."""
    data_processamento: datetime

class BuscaLicitacoesRequest(BaseModel):
    """
    Modelo para requisição de busca manual de licitações.
    Permite filtrar licitações por data inicial e final.
    """
    data_inicial: Optional[str] = None
    data_final: Optional[str] = None

# Instancia a aplicação FastAPI
app = FastAPI(title="API de Gestão de Licitações Correio MVP")

# Habilitar CORS para que o frontend React possa se comunicar
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Permite o domínio do frontend React
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """
    Evento executado ao iniciar a API. Garante que as tabelas do banco estejam criadas
    e configura a chave da OpenAI a partir das variáveis de ambiente.
    """
    create_db_tables()
    print("API Iniciada e tabelas do DB verificadas/criadas.")
    # Configuração do OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    openai.api_key = OPENAI_API_KEY

@app.get("/api/licitacoes/", response_model=List[LicitacaoResponse])
def read_licitacoes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retorna uma lista de licitações processadas.
    Parâmetros:
        skip (int): Quantidade de registros a pular (paginação).
        limit (int): Quantidade máxima de registros a retornar.
        db (Session): Sessão do banco de dados.
    Retorno:
        Lista de licitações processadas.
    """
    licitacoes = db.query(Licitacao).offset(skip).limit(limit).all()
    return licitacoes

@app.get("/api/licitacoes/{licitacao_id}", response_model=LicitacaoResponse)
def read_licitacao(licitacao_id: str, db: Session = Depends(get_db)):
    """
    Retorna uma licitação específica pelo ID.
    Parâmetros:
        licitacao_id (str): ID da licitação.
        db (Session): Sessão do banco de dados.
    Retorno:
        Dados completos da licitação.
    """
    licitacao = db.query(Licitacao).filter(Licitacao.id == licitacao_id).first()
    if licitacao is None:
        raise HTTPException(status_code=404, detail="Licitação não encontrada")
    return licitacao

@app.post("/api/processar_licitacoes/", status_code=202)
def trigger_licitacao_processing():
    """
    Aciona o processo de busca e processamento de novas licitações pela CrewAI.
    No MVP, apenas simula a ação e retorna uma mensagem de confirmação.
    """
    print("Requisição para processar novas licitações recebida. Acionando Crew (simulado).")
    return {"message": "Processamento de licitações acionado. Verifique os logs do backend."}

@app.post("/api/forcar_busca_licitacoes/")
def forcar_busca_licitacoes(request: BuscaLicitacoesRequest = Body(...)):
    """
    Endpoint para forçar a busca manual de licitações via CrewAI.
    Executa scraping e retorna os resultados encontrados conforme datas informadas.
    """
    licitacoes = asyncio.run(search_new_licitacoes_correios(
        data_inicial=request.data_inicial,
        data_final=request.data_final
    ))
    return {"licitacoes": licitacoes}

@app.post("/api/gerar_analise")
def gerar_analise_licitacao(id: str = Query(...), db: Session = Depends(get_db)):
    """
    Gera análise automática (jurídica, risco, mercado, cambial, resumo e recomendação) para a licitação informada.
    Utiliza a API da OpenAI para gerar textos inteligentes e salva os resultados no banco.
    Parâmetros:
        id (str): ID da licitação a ser analisada.
        db (Session): Sessão do banco de dados.
    Retorno:
        Objeto da licitação atualizado com as análises.
    """
    lic = db.query(Licitacao).filter(Licitacao.id == id).first()
    if not lic:
        raise HTTPException(status_code=404, detail="Licitação não encontrada")
    # Função auxiliar para consultar a OpenAI
    def chatgpt(prompt):
        """
        Envia um prompt para a API da OpenAI e retorna a resposta gerada.
        """
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=600
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[Erro ao gerar análise: {e}]"
    objeto = lic.objeto or ""
    lic.analise_juridica_texto = chatgpt(f"Faça uma análise jurídica detalhada do seguinte objeto de licitação: {objeto}")
    lic.pontos_de_atencao_juridica = [
        chatgpt(f"Liste os principais pontos de atenção jurídica para o seguinte objeto de licitação, em frases curtas: {objeto}")
    ]
    lic.risco_geral = chatgpt(f"Classifique o risco geral (baixo, médio ou alto) para a seguinte licitação e justifique em 1 frase: {objeto}")
    lic.analise_cambial_texto = chatgpt(f"Existe algum impacto cambial relevante para o seguinte objeto de licitação? Responda de forma sucinta: {objeto}")
    lic.analise_mercado_texto = chatgpt(f"Faça uma análise de mercado para o seguinte objeto de licitação: {objeto}")
    lic.resumo_executivo_gerencial = chatgpt(f"Faça um resumo executivo gerencial para a seguinte licitação: {objeto}")
    lic.recomendacao_final = chatgpt(f"Dê uma recomendação final para a seguinte licitação, considerando riscos e oportunidades: {objeto}")
    db.commit()
    db.refresh(lic)
    return lic

if __name__ == "__main__":
    # Permite rodar a API localmente para desenvolvimento
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) # reload=True para desenvolvimento