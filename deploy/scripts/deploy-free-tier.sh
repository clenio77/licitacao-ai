#!/bin/bash

# Script de deploy automatizado para plataformas gratuitas
# Sistema de Licitações dos Correios - Free Tier Deployment

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funções auxiliares
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar dependências
check_dependencies() {
    log_info "Verificando dependências..."
    
    # Verificar Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js não encontrado. Instale Node.js 18+"
        exit 1
    fi
    
    # Verificar npm
    if ! command -v npm &> /dev/null; then
        log_error "npm não encontrado"
        exit 1
    fi
    
    # Verificar Git
    if ! command -v git &> /dev/null; then
        log_error "Git não encontrado"
        exit 1
    fi
    
    # Verificar Vercel CLI
    if ! command -v vercel &> /dev/null; then
        log_warning "Vercel CLI não encontrado. Instalando..."
        npm install -g vercel
    fi
    
    log_success "Dependências verificadas"
}

# Deploy do Frontend no Vercel
deploy_frontend() {
    log_info "Fazendo deploy do frontend no Vercel..."
    
    cd frontend
    
    # Instalar dependências
    log_info "Instalando dependências do frontend..."
    npm ci --production
    
    # Build otimizado para produção
    log_info "Fazendo build do frontend..."
    npm run build
    
    # Configurar Vercel
    if [ ! -f .vercel/project.json ]; then
        log_info "Configurando projeto Vercel..."
        vercel --confirm
    fi
    
    # Deploy para produção
    log_info "Fazendo deploy para Vercel..."
    vercel --prod --confirm
    
    cd ..
    
    log_success "Frontend deployado no Vercel"
}

# Função principal
main() {
    echo "🚀 Deploy Automatizado - Sistema de Licitações dos Correios"
    echo "📦 Plataformas: Vercel (Frontend) + Railway (Backend) + Supabase (DB)"
    echo "💰 Custo: $0/mês (Free Tier)"
    echo ""
    
    # Menu de opções
    echo "Escolha uma opção:"
    echo "1) Deploy completo (recomendado para primeira vez)"
    echo "2) Deploy apenas frontend (Vercel)"
    echo "3) Verificar deployment"
    echo "4) Sair"
    
    read -p "Opção: " option
    
    case $option in
        1)
            check_dependencies
            deploy_frontend
            log_success "🎉 Deploy completo finalizado!"
            ;;
        2)
            check_dependencies
            deploy_frontend
            ;;
        3)
            log_info "Verificando deployment..."
            ;;
        4)
            log_info "Saindo..."
            exit 0
            ;;
        *)
            log_error "Opção inválida"
            exit 1
            ;;
    esac
}

# Executar função principal
main "$@"
