#!/usr/bin/env python3
"""
Script de teste para verificar o funcionamento do sistema.
Execute: python3 test_sistema.py
"""

import requests
import json
import sys
import os
from datetime import datetime

# Configurações
API_BASE_URL = "http://localhost:8000/api"
FRONTEND_URL = "http://localhost:3000"

def test_backend_health():
    """Testa se o backend está rodando"""
    try:
        response = requests.get(f"{API_BASE_URL}/licitacoes/", timeout=5)
        if response.status_code == 200:
            print("✅ Backend está rodando e respondendo")
            return True
        else:
            print(f"❌ Backend retornou status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao conectar com o backend: {e}")
        return False

def test_frontend_health():
    """Testa se o frontend está rodando"""
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print("✅ Frontend está rodando")
            return True
        else:
            print(f"❌ Frontend retornou status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao conectar com o frontend: {e}")
        return False

def test_database():
    """Testa se o banco de dados está acessível"""
    try:
        # Tenta acessar endpoint que usa o banco
        response = requests.get(f"{API_BASE_URL}/licitacoes/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Banco de dados acessível ({len(data)} licitações)")
            return True
        else:
            print("❌ Erro ao acessar o banco de dados")
            return False
    except Exception as e:
        print(f"❌ Erro no banco de dados: {e}")
        return False

def test_openai_config():
    """Testa se a configuração do OpenAI está correta"""
    try:
        # Verifica se a variável está definida
        env_file = "backend/.env"
        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                content = f.read()
                if "OPENAI_API_KEY" in content and "sua_chave" not in content:
                    print("✅ OpenAI API Key configurada")
                    return True
                else:
                    print("⚠️  OpenAI API Key não configurada no .env")
                    return False
        else:
            print("⚠️  Arquivo .env não encontrado")
            return False
    except Exception as e:
        print(f"❌ Erro ao verificar OpenAI config: {e}")
        return False

def test_endpoints():
    """Testa endpoints principais"""
    endpoints = [
        ("/licitacoes/", "GET", "Listar licitações"),
        ("/editais/", "GET", "Listar editais"),
        ("/feedback/analytics/dashboard", "GET", "Dashboard de feedback"),
        ("/scraping/status", "GET", "Status do scraping"),
        ("/requisicoes/", "GET", "Listar requisições")
    ]
    
    results = []
    for endpoint, method, description in endpoints:
        try:
            response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=5)
            if response.status_code in [200, 404]:  # 404 é ok para endpoints vazios
                print(f"✅ {description}: OK")
                results.append(True)
            else:
                print(f"❌ {description}: Status {response.status_code}")
                results.append(False)
        except Exception as e:
            print(f"❌ {description}: Erro {e}")
            results.append(False)
    
    return all(results)

def test_file_structure():
    """Verifica se a estrutura de arquivos está correta"""
    required_files = [
        "backend/api/app.py",
        "backend/api/database.py",
        "backend/api/edital_endpoints.py",
        "backend/api/feedback_endpoints.py",
        "backend/api/scraping_endpoints.py",
        "backend/api/requisicoes_endpoints.py",
        "frontend/src/App.js",
        "frontend/src/pages/GerarEdital.js",
        "frontend/src/pages/BaseConhecimento.js",
        "frontend/src/pages/Feedback.js",
        "frontend/package.json",
        "backend/requirements.txt"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Arquivos faltando: {missing_files}")
        return False
    else:
        print("✅ Estrutura de arquivos correta")
        return True

def main():
    """Função principal de teste"""
    print("🔍 Testando Sistema de Licitações dos Correios")
    print("=" * 50)
    
    tests = [
        ("Estrutura de arquivos", test_file_structure),
        ("Configuração OpenAI", test_openai_config),
        ("Backend Health", test_backend_health),
        ("Frontend Health", test_frontend_health),
        ("Banco de dados", test_database),
        ("Endpoints da API", test_endpoints)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🧪 Testando: {test_name}")
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"❌ Erro no teste {test_name}: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 RESUMO DOS TESTES")
    print("=" * 50)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema está funcionando corretamente")
    else:
        print(f"⚠️  {passed}/{total} testes passaram")
        print("❌ Alguns componentes precisam de atenção")
    
    print("\n📋 PRÓXIMOS PASSOS:")
    if passed < total:
        print("1. Verificar logs do backend e frontend")
        print("2. Consultar SETUP_RAPIDO.md para troubleshooting")
        print("3. Verificar configurações no .env")
    else:
        print("1. Sistema pronto para uso!")
        print("2. Acesse http://localhost:3000")
        print("3. Consulte STATUS_IMPLEMENTACAO.md para mais detalhes")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)