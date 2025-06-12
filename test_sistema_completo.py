#!/usr/bin/env python3
"""
Script de teste completo do sistema de licitações dos Correios.
Testa todas as funcionalidades principais.
"""

import asyncio
import json
import requests
import time
from datetime import datetime

# Configurações
API_BASE_URL = "http://localhost:8000/api"
FRONTEND_URL = "http://localhost:3000"

def print_header(title):
    """Imprime cabeçalho formatado"""
    print("\n" + "="*60)
    print(f"🧪 {title}")
    print("="*60)

def print_step(step, description):
    """Imprime passo do teste"""
    print(f"\n{step}. {description}")
    print("-" * 40)

def test_api_health():
    """Testa se a API está funcionando"""
    print_header("TESTE DE CONECTIVIDADE")
    
    try:
        response = requests.get(f"{API_BASE_URL}/licitacoes", timeout=5)
        if response.status_code == 200:
            print("✅ API Backend está funcionando")
            return True
        else:
            print(f"❌ API retornou status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Erro ao conectar com API: {str(e)}")
        return False

def test_base_conhecimento():
    """Testa funcionalidades da base de conhecimento"""
    print_header("TESTE DA BASE DE CONHECIMENTO")
    
    # Teste 1: Resumo da base
    print_step(1, "Testando resumo da base de conhecimento")
    try:
        response = requests.get(f"{API_BASE_URL}/scraping/base-conhecimento/resumo")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Total de licitações na base: {data.get('total_licitacoes', 0)}")
            print(f"✅ Categorias disponíveis: {list(data.get('distribuicao_categorias', {}).keys())}")
        else:
            print(f"❌ Erro ao obter resumo: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
    
    # Teste 2: Consulta da base
    print_step(2, "Testando consulta da base de conhecimento")
    try:
        params = {
            'categoria': 'servicos',
            'objeto': 'limpeza',
            'tipo_licitacao': 'pregao'
        }
        response = requests.get(f"{API_BASE_URL}/scraping/base-conhecimento/consultar", params=params)
        if response.status_code == 200:
            data = response.json()
            encontradas = data.get('dados', {}).get('encontradas', 0)
            print(f"✅ Consulta realizada: {encontradas} licitações similares encontradas")
            
            # Mostrar insights se disponíveis
            insights = data.get('dados', {}).get('insights', {})
            if insights:
                fatores = insights.get('fatores_sucesso_comuns', [])
                if fatores:
                    print(f"✅ Fatores de sucesso identificados: {len(fatores)}")
        else:
            print(f"❌ Erro na consulta: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
    
    # Teste 3: Analytics
    print_step(3, "Testando analytics da base")
    try:
        response = requests.get(f"{API_BASE_URL}/scraping/base-conhecimento/analytics?tipo_analise=geral")
        if response.status_code == 200:
            data = response.json()
            print("✅ Analytics gerado com sucesso")
            if data.get('dados', {}).get('total_licitacoes'):
                print(f"✅ Total analisado: {data['dados']['total_licitacoes']} licitações")
        else:
            print(f"❌ Erro no analytics: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {str(e)}")

def test_geracao_edital():
    """Testa geração de edital"""
    print_header("TESTE DE GERAÇÃO DE EDITAL")
    
    # Dados de teste para geração de edital
    edital_data = {
        "objeto": "Contratação de serviços de limpeza predial para teste",
        "tipo_licitacao": "pregao",
        "modalidade": "eletronica",
        "categoria": "servicos",
        "setor_requisitante": {
            "nome": "Gerência de Teste",
            "responsavel": "João Teste",
            "email": "joao.teste@correios.com.br",
            "telefone": "(11) 99999-9999",
            "justificativa": "Teste do sistema de geração automatizada"
        },
        "itens": [
            {
                "numero": 1,
                "descricao": "Serviços de limpeza predial",
                "unidade": "m²",
                "quantidade": 1000,
                "valor_estimado_unitario": 5.0,
                "categoria": "servicos"
            }
        ],
        "valor_total_estimado": 5000.0,
        "prazo_execucao": 365,
        "prazo_proposta": 8,
        "permite_consorcio": False,
        "exige_visita_tecnica": False,
        "criterio_julgamento": "menor_preco",
        "observacoes": "Edital de teste gerado automaticamente"
    }
    
    print_step(1, "Iniciando geração de edital")
    try:
        response = requests.post(f"{API_BASE_URL}/editais/gerar", json=edital_data)
        if response.status_code == 200:
            data = response.json()
            request_id = data.get('request_id')
            print(f"✅ Geração iniciada com sucesso")
            print(f"✅ Request ID: {request_id}")
            
            # Aguardar processamento
            print_step(2, "Aguardando processamento (30 segundos)")
            time.sleep(30)
            
            # Verificar status
            print_step(3, "Verificando status do processamento")
            status_response = requests.get(f"{API_BASE_URL}/editais/status/{request_id}")
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"✅ Status: {status_data.get('status')}")
                
                if status_data.get('edital_disponivel'):
                    edital_id = status_data.get('edital_id')
                    print(f"✅ Edital gerado com ID: {edital_id}")
                    
                    # Obter edital gerado
                    print_step(4, "Obtendo edital gerado")
                    edital_response = requests.get(f"{API_BASE_URL}/editais/{edital_id}")
                    if edital_response.status_code == 200:
                        edital_data = edital_response.json()
                        print("✅ Edital obtido com sucesso")
                        print(f"✅ Tamanho do conteúdo: {len(edital_data.get('conteudo_edital', ''))} caracteres")
                    else:
                        print(f"❌ Erro ao obter edital: {edital_response.status_code}")
                else:
                    print("⚠️ Edital ainda em processamento")
            else:
                print(f"❌ Erro ao verificar status: {status_response.status_code}")
        else:
            print(f"❌ Erro ao iniciar geração: {response.status_code}")
            print(f"Resposta: {response.text}")
    except Exception as e:
        print(f"❌ Erro: {str(e)}")

def test_scraping():
    """Testa execução de scraping"""
    print_header("TESTE DE WEB SCRAPING")
    
    print_step(1, "Executando scraping de teste")
    try:
        scraping_data = {
            "categorias": ["serviços de limpeza", "equipamentos de informática"],
            "salvar_automatico": True
        }
        
        response = requests.post(f"{API_BASE_URL}/scraping/executar", json=scraping_data)
        if response.status_code == 200:
            data = response.json()
            print("✅ Scraping iniciado com sucesso")
            print(f"✅ Categorias: {data.get('categorias', [])}")
            print("ℹ️ Dados serão coletados em background")
        else:
            print(f"❌ Erro ao executar scraping: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {str(e)}")

def test_licitacoes_originais():
    """Testa funcionalidade original de licitações"""
    print_header("TESTE DE LICITAÇÕES (FUNCIONALIDADE ORIGINAL)")
    
    print_step(1, "Listando licitações existentes")
    try:
        response = requests.get(f"{API_BASE_URL}/licitacoes")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {len(data)} licitações encontradas")
        else:
            print(f"❌ Erro ao listar licitações: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {str(e)}")

def test_templates():
    """Testa templates de editais"""
    print_header("TESTE DE TEMPLATES")
    
    print_step(1, "Listando templates disponíveis")
    try:
        response = requests.get(f"{API_BASE_URL}/editais/templates/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ {len(data)} templates encontrados")
            for template in data[:3]:  # Mostrar apenas os 3 primeiros
                print(f"  - {template.get('nome')} ({template.get('categoria')})")
        else:
            print(f"❌ Erro ao listar templates: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro: {str(e)}")

def main():
    """Função principal de teste"""
    print("🚀 INICIANDO TESTE COMPLETO DO SISTEMA DE LICITAÇÕES DOS CORREIOS")
    print(f"⏰ Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Teste 1: Conectividade
    if not test_api_health():
        print("\n❌ Sistema não está funcionando. Verifique se o backend está rodando.")
        return
    
    # Teste 2: Funcionalidade original
    test_licitacoes_originais()
    
    # Teste 3: Templates
    test_templates()
    
    # Teste 4: Base de conhecimento
    test_base_conhecimento()
    
    # Teste 5: Web scraping
    test_scraping()
    
    # Teste 6: Geração de edital (mais demorado)
    print("\n⚠️ O próximo teste (geração de edital) pode demorar alguns minutos...")
    input("Pressione Enter para continuar ou Ctrl+C para pular...")
    test_geracao_edital()
    
    # Resumo final
    print_header("RESUMO DOS TESTES")
    print("✅ Testes de conectividade concluídos")
    print("✅ Testes de funcionalidades básicas concluídos")
    print("✅ Testes de base de conhecimento concluídos")
    print("✅ Testes de web scraping concluídos")
    print("✅ Testes de geração de edital concluídos")
    
    print(f"\n🎉 TESTE COMPLETO FINALIZADO - {datetime.now().strftime('%H:%M:%S')}")
    print("\n📋 PRÓXIMOS PASSOS:")
    print("1. Acesse o frontend em http://localhost:3000")
    print("2. Teste a interface web completa")
    print("3. Execute scraping periódico para manter base atualizada")
    print("4. Configure agendamento automático de coleta")

if __name__ == "__main__":
    main()
