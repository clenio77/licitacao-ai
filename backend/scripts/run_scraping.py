#!/usr/bin/env python3
"""
Script para executar web scraping e popular a base de conhecimento.
Pode ser executado manualmente ou agendado via cron.
"""

import asyncio
import sys
import os
from datetime import datetime

# Adicionar o diretório pai ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web_scraping.gov_procurement_scraper import GovProcurementScraper

async def main():
    """Função principal para executar o scraping"""
    print("🚀 Iniciando coleta de dados de licitações bem-sucedidas...")
    print(f"⏰ Data/Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Categorias para coletar
    categorias_prioritarias = [
        'serviços de limpeza',
        'equipamentos de informática',
        'material de escritório',
        'serviços de segurança',
        'serviços de manutenção',
        'veículos',
        'combustível',
        'serviços de telecomunicações',
        'móveis e utensílios',
        'material de construção'
    ]
    
    try:
        # Criar instância do scraper
        scraper = GovProcurementScraper()
        
        # Executar scraping
        print(f"🔍 Coletando dados para {len(categorias_prioritarias)} categorias...")
        licitacoes = await scraper.scrape_all_sites(categorias_prioritarias)
        
        if licitacoes:
            # Salvar na base de conhecimento
            filepath = await scraper.save_to_knowledge_base(licitacoes)
            
            print(f"✅ Scraping concluído com sucesso!")
            print(f"📊 Total de licitações coletadas: {len(licitacoes)}")
            print(f"💾 Dados salvos em: {filepath}")
            
            # Estatísticas por categoria
            categorias_count = {}
            for lic in licitacoes:
                cat = lic.categoria
                categorias_count[cat] = categorias_count.get(cat, 0) + 1
            
            print("\n📈 Distribuição por categoria:")
            for categoria, count in categorias_count.items():
                print(f"  - {categoria}: {count} licitações")
            
            # Estatísticas por site
            sites_count = {}
            for lic in licitacoes:
                site = lic.site_origem
                sites_count[site] = sites_count.get(site, 0) + 1
            
            print("\n🌐 Distribuição por site:")
            for site, count in sites_count.items():
                print(f"  - {site}: {count} licitações")
                
        else:
            print("⚠️ Nenhuma licitação foi coletada")
            print("💡 Verifique a conectividade e disponibilidade dos sites")
            
    except Exception as e:
        print(f"❌ Erro durante o scraping: {str(e)}")
        sys.exit(1)
    
    print(f"\n🏁 Processo finalizado em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    # Verificar se o diretório data existe
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"📁 Diretório {data_dir} criado")
    
    # Executar scraping
    asyncio.run(main())
