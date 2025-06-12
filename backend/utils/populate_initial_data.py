"""
Script para popular o banco de dados com dados iniciais.
Inclui templates de editais e histórico de licitações.
"""

import json
import os
import sys
from datetime import datetime
import uuid

# Adicionar o diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.database import SessionLocal, create_db_tables, TemplateEdital, HistoricoEdital

def populate_templates():
    """Popula templates de editais no banco de dados"""
    db = SessionLocal()
    
    try:
        # Template para serviços - pregão
        template_servicos = TemplateEdital(
            id=str(uuid.uuid4()),
            nome="Template Padrão - Serviços (Pregão)",
            categoria="servicos",
            tipo_licitacao="pregao",
            conteudo_template=load_template_file("template_servicos_pregao.txt"),
            variaveis=[
                "{{NUMERO_EDITAL}}", "{{OBJETO}}", "{{DESCRICAO_DETALHADA}}",
                "{{VALOR_ESTIMADO}}", "{{VALOR_ESTIMADO_EXTENSO}}", "{{PRAZO_EXECUCAO}}",
                "{{DATA_LIMITE_PROPOSTAS}}", "{{DATA_SESSAO_PUBLICA}}", "{{PERMITE_CONSORCIO}}",
                "{{REQUISITOS_HABILITACAO}}", "{{ESPECIFICACOES_TECNICAS}}", "{{ESPECIFICACOES_DETALHADAS}}",
                "{{CRITERIO_JULGAMENTO}}", "{{OBRIGACOES_ESPECIFICAS}}", "{{CONDICOES_PAGAMENTO}}",
                "{{DISPOSICOES_GERAIS}}", "{{LOCAL_DATA}}", "{{NOME_PREGOEIRO}}"
            ],
            ativo=True,
            versao="1.0",
            criado_por="sistema",
            vezes_usado=0,
            taxa_sucesso=0.75
        )
        
        # Template para bens - pregão
        template_bens = TemplateEdital(
            id=str(uuid.uuid4()),
            nome="Template Padrão - Bens (Pregão)",
            categoria="bens",
            tipo_licitacao="pregao",
            conteudo_template=create_template_bens(),
            variaveis=[
                "{{NUMERO_EDITAL}}", "{{OBJETO}}", "{{DESCRICAO_DETALHADA}}",
                "{{VALOR_ESTIMADO}}", "{{PRAZO_ENTREGA}}", "{{ESPECIFICACOES_TECNICAS}}",
                "{{CRITERIO_JULGAMENTO}}", "{{LOCAL_ENTREGA}}"
            ],
            ativo=True,
            versao="1.0",
            criado_por="sistema",
            vezes_usado=0,
            taxa_sucesso=0.80
        )
        
        # Template para obras - concorrência
        template_obras = TemplateEdital(
            id=str(uuid.uuid4()),
            nome="Template Padrão - Obras (Concorrência)",
            categoria="obras",
            tipo_licitacao="concorrencia",
            conteudo_template=create_template_obras(),
            variaveis=[
                "{{NUMERO_EDITAL}}", "{{OBJETO}}", "{{DESCRICAO_DETALHADA}}",
                "{{VALOR_ESTIMADO}}", "{{PRAZO_EXECUCAO}}", "{{LOCAL_OBRA}}",
                "{{ESPECIFICACOES_TECNICAS}}", "{{QUALIFICACAO_TECNICA}}"
            ],
            ativo=True,
            versao="1.0",
            criado_por="sistema",
            vezes_usado=0,
            taxa_sucesso=0.70
        )
        
        # Verificar se templates já existem
        existing_templates = db.query(TemplateEdital).count()
        if existing_templates == 0:
            db.add(template_servicos)
            db.add(template_bens)
            db.add(template_obras)
            db.commit()
            print(f"✅ {3} templates adicionados ao banco de dados")
        else:
            print(f"ℹ️ Templates já existem no banco ({existing_templates} encontrados)")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao popular templates: {str(e)}")
    finally:
        db.close()

def populate_historico():
    """Popula histórico de editais no banco de dados"""
    db = SessionLocal()
    
    try:
        # Carregar dados do histórico
        historico_data = load_historico_file()
        
        existing_historico = db.query(HistoricoEdital).count()
        if existing_historico == 0:
            for item in historico_data:
                historico = HistoricoEdital(
                    id=str(uuid.uuid4()),
                    id_edital=item['id_edital'],
                    objeto=item['objeto'],
                    categoria=item['categoria'],
                    tipo_licitacao=item['tipo_licitacao'],
                    sucesso=item['sucesso'],
                    motivo_fracasso=item.get('motivo_fracasso'),
                    licoes_aprendidas=item.get('licoes_aprendidas', []),
                    data_resultado=datetime.fromisoformat(item['data_resultado'].replace('Z', '+00:00')),
                    valor_contratado=item.get('valor_contratado'),
                    numero_propostas=item.get('numero_propostas'),
                    fatores_sucesso=item.get('fatores_sucesso', []),
                    fatores_fracasso=item.get('fatores_fracasso', []),
                    criado_por="sistema"
                )
                db.add(historico)
            
            db.commit()
            print(f"✅ {len(historico_data)} registros de histórico adicionados")
        else:
            print(f"ℹ️ Histórico já existe no banco ({existing_historico} registros)")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Erro ao popular histórico: {str(e)}")
    finally:
        db.close()

def load_template_file(filename):
    """Carrega arquivo de template"""
    template_path = os.path.join("data", "templates_editais", filename)
    if os.path.exists(template_path):
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        print(f"⚠️ Template {filename} não encontrado, usando template básico")
        return create_basic_template()

def load_historico_file():
    """Carrega arquivo de histórico"""
    historico_path = os.path.join("data", "historico_editais.json")
    if os.path.exists(historico_path):
        with open(historico_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        print("⚠️ Arquivo de histórico não encontrado, usando dados básicos")
        return []

def create_basic_template():
    """Cria template básico se arquivo não existir"""
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

def create_template_bens():
    """Cria template específico para bens"""
    return """
EDITAL DE PREGÃO ELETRÔNICO Nº {{NUMERO_EDITAL}}

EMPRESA BRASILEIRA DE CORREIOS E TELÉGRAFOS

PREGÃO ELETRÔNICO PARA AQUISIÇÃO DE {{OBJETO}}

1. DO OBJETO
1.1. Aquisição de {{DESCRICAO_DETALHADA}}, conforme especificações deste Edital.

2. DO VALOR ESTIMADO
2.1. Valor total estimado: R$ {{VALOR_ESTIMADO}}

3. DOS PRAZOS
3.1. Prazo para entrega: {{PRAZO_ENTREGA}} dias corridos
3.2. Local de entrega: {{LOCAL_ENTREGA}}

4. DAS ESPECIFICAÇÕES TÉCNICAS
{{ESPECIFICACOES_TECNICAS}}

5. DO CRITÉRIO DE JULGAMENTO
5.1. {{CRITERIO_JULGAMENTO}}

6. DAS DISPOSIÇÕES GERAIS
6.1. Rege-se pela Lei 14.133/2021
"""

def create_template_obras():
    """Cria template específico para obras"""
    return """
EDITAL DE CONCORRÊNCIA Nº {{NUMERO_EDITAL}}

EMPRESA BRASILEIRA DE CORREIOS E TELÉGRAFOS

CONCORRÊNCIA PARA EXECUÇÃO DE {{OBJETO}}

1. DO OBJETO
1.1. Execução de {{DESCRICAO_DETALHADA}}

2. DO VALOR ESTIMADO
2.1. Valor total estimado: R$ {{VALOR_ESTIMADO}}

3. DOS PRAZOS
3.1. Prazo para execução: {{PRAZO_EXECUCAO}} dias
3.2. Local da obra: {{LOCAL_OBRA}}

4. DA QUALIFICAÇÃO TÉCNICA
{{QUALIFICACAO_TECNICA}}

5. DAS ESPECIFICAÇÕES TÉCNICAS
{{ESPECIFICACOES_TECNICAS}}

6. DAS DISPOSIÇÕES GERAIS
6.1. Rege-se pela Lei 14.133/2021
"""

def main():
    """Função principal para popular dados iniciais"""
    print("🚀 Iniciando população de dados iniciais...")
    
    # Criar tabelas se não existirem
    create_db_tables()
    print("✅ Tabelas verificadas/criadas")
    
    # Popular templates
    print("\n📝 Populando templates de editais...")
    populate_templates()
    
    # Popular histórico
    print("\n📊 Populando histórico de editais...")
    populate_historico()
    
    print("\n🎉 População de dados iniciais concluída!")

if __name__ == "__main__":
    main()
