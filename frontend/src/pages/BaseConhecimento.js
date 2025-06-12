import React, { useState, useEffect } from 'react';
import './BaseConhecimento.css';

const BaseConhecimento = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [conhecimentos, setConhecimentos] = useState([]);
  const [analytics, setAnalytics] = useState({
    total_documentos: 0,
    padroes_sucesso: 0,
    ultima_atualizacao: '',
    taxa_sucesso: 0
  });

  // Simular dados da base de conhecimento
  useEffect(() => {
    const mockData = [
      {
        id: 1,
        titulo: 'Padrão de Sucesso - Licitação de Serviços de Limpeza',
        categoria: 'servicos',
        tipo: 'padrao_sucesso',
        fonte: 'Portal Nacional de Contratações Públicas',
        data_coleta: '2024-01-15',
        valor_contrato: 'R$ 2.500.000,00',
        prazo_execucao: '12 meses',
        modalidade: 'Pregão Eletrônico',
        criterio_julgamento: 'Menor Preço',
        numero_propostas: 15,
        economia_obtida: '18%',
        pontos_chave: [
          'Especificações técnicas detalhadas e objetivas',
          'Critérios de sustentabilidade bem definidos',
          'Exigência de certificações ambientais',
          'Planilha de custos e formação de preços clara'
        ],
        observacoes: 'Licitação bem-sucedida com alta participação e economia significativa.',
        url_original: 'https://pncp.gov.br/app/editais/12345'
      },
      {
        id: 2,
        titulo: 'Análise - Licitação de Equipamentos de TI',
        categoria: 'ti',
        tipo: 'analise_mercado',
        fonte: 'ComprasNet',
        data_coleta: '2024-01-14',
        valor_contrato: 'R$ 850.000,00',
        modalidade: 'Pregão Eletrônico',
        criterio_julgamento: 'Menor Preço',
        numero_propostas: 8,
        economia_obtida: '12%',
        pontos_chave: [
          'Especificações baseadas em performance',
          'Garantia estendida obrigatória',
          'Suporte técnico local exigido',
          'Compatibilidade com infraestrutura existente'
        ],
        observacoes: 'Boa participação do mercado, especificações adequadas.',
        url_original: 'https://comprasnet.gov.br/consultas/12346'
      },
      {
        id: 3,
        titulo: 'Padrão de Sucesso - Obras de Reforma Predial',
        categoria: 'obras',
        tipo: 'padrao_sucesso',
        fonte: 'Portal da Transparência',
        data_coleta: '2024-01-13',
        valor_contrato: 'R$ 1.200.000,00',
        prazo_execucao: '8 meses',
        modalidade: 'Concorrência',
        criterio_julgamento: 'Técnica e Preço',
        numero_propostas: 6,
        economia_obtida: '15%',
        pontos_chave: [
          'Projeto executivo detalhado',
          'Cronograma físico-financeiro realista',
          'Exigência de visita técnica obrigatória',
          'Garantia de 5 anos para a obra'
        ],
        observacoes: 'Obra executada dentro do prazo e orçamento previsto.',
        url_original: 'https://transparencia.gov.br/licitacoes/12347'
      }
    ];

    setConhecimentos(mockData);
    setAnalytics({
      total_documentos: mockData.length,
      padroes_sucesso: mockData.filter(item => item.tipo === 'padrao_sucesso').length,
      ultima_atualizacao: '2024-01-15',
      taxa_sucesso: 87.5
    });
  }, []);

  const filteredConhecimentos = conhecimentos.filter(item => {
    const matchesSearch = item.titulo.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.pontos_chave.some(ponto => ponto.toLowerCase().includes(searchTerm.toLowerCase()));
    const matchesCategory = selectedCategory === 'all' || item.categoria === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  const renderDashboard = () => (
    <div className="conhecimento-dashboard">
      <div className="analytics-cards">
        <div className="analytics-card">
          <div className="card-icon">📚</div>
          <div className="card-content">
            <h3>Total de Documentos</h3>
            <div className="metric-value">{analytics.total_documentos}</div>
            <div className="metric-label">Na base de conhecimento</div>
          </div>
        </div>

        <div className="analytics-card">
          <div className="card-icon">⭐</div>
          <div className="card-content">
            <h3>Padrões de Sucesso</h3>
            <div className="metric-value">{analytics.padroes_sucesso}</div>
            <div className="metric-label">Licitações bem-sucedidas</div>
          </div>
        </div>

        <div className="analytics-card">
          <div className="card-icon">📈</div>
          <div className="card-content">
            <h3>Taxa de Sucesso</h3>
            <div className="metric-value">{analytics.taxa_sucesso}%</div>
            <div className="metric-label">Baseada nos padrões</div>
          </div>
        </div>

        <div className="analytics-card">
          <div className="card-icon">🔄</div>
          <div className="card-content">
            <h3>Última Atualização</h3>
            <div className="metric-value">{analytics.ultima_atualizacao}</div>
            <div className="metric-label">Dados atualizados</div>
          </div>
        </div>
      </div>

      <div className="knowledge-stats">
        <div className="stats-container">
          <h3>📊 Distribuição por Categoria</h3>
          <div className="category-stats">
            <div className="category-stat">
              <span className="category-label">Serviços</span>
              <div className="stat-bar">
                <div className="stat-fill" style={{width: '40%'}}></div>
              </div>
              <span className="stat-value">40%</span>
            </div>
            <div className="category-stat">
              <span className="category-label">TI</span>
              <div className="stat-bar">
                <div className="stat-fill" style={{width: '30%'}}></div>
              </div>
              <span className="stat-value">30%</span>
            </div>
            <div className="category-stat">
              <span className="category-label">Obras</span>
              <div className="stat-bar">
                <div className="stat-fill" style={{width: '20%'}}></div>
              </div>
              <span className="stat-value">20%</span>
            </div>
            <div className="category-stat">
              <span className="category-label">Outros</span>
              <div className="stat-bar">
                <div className="stat-fill" style={{width: '10%'}}></div>
              </div>
              <span className="stat-value">10%</span>
            </div>
          </div>
        </div>

        <div className="stats-container">
          <h3>🎯 Principais Insights</h3>
          <div className="insights-list">
            <div className="insight-item">
              <span className="insight-icon">💡</span>
              <div className="insight-content">
                <div className="insight-title">Especificações Detalhadas</div>
                <div className="insight-desc">Aumentam participação em 25%</div>
              </div>
            </div>
            <div className="insight-item">
              <span className="insight-icon">🌱</span>
              <div className="insight-content">
                <div className="insight-title">Critérios Sustentáveis</div>
                <div className="insight-desc">Presentes em 80% dos sucessos</div>
              </div>
            </div>
            <div className="insight-item">
              <span className="insight-icon">⚖️</span>
              <div className="insight-content">
                <div className="insight-title">Julgamento por Menor Preço</div>
                <div className="insight-desc">Modalidade mais eficiente</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderConhecimentoCard = (item) => (
    <div key={item.id} className="conhecimento-card">
      <div className="card-header">
        <div className="card-title">
          <h4>{item.titulo}</h4>
          <div className="card-badges">
            <span className={`badge badge-${item.categoria}`}>
              {item.categoria.toUpperCase()}
            </span>
            <span className={`badge badge-${item.tipo}`}>
              {item.tipo === 'padrao_sucesso' ? 'SUCESSO' : 'ANÁLISE'}
            </span>
          </div>
        </div>
        <div className="card-meta">
          <span className="meta-item">📅 {item.data_coleta}</span>
          <span className="meta-item">💰 {item.valor_contrato}</span>
          <span className="meta-item">📊 {item.numero_propostas} propostas</span>
        </div>
      </div>

      <div className="card-content">
        <div className="content-section">
          <h5>🎯 Pontos-Chave de Sucesso</h5>
          <ul className="pontos-chave">
            {item.pontos_chave.map((ponto, index) => (
              <li key={index}>{ponto}</li>
            ))}
          </ul>
        </div>

        <div className="content-section">
          <h5>📋 Detalhes da Licitação</h5>
          <div className="detalhes-grid">
            <div className="detalhe-item">
              <strong>Modalidade:</strong> {item.modalidade}
            </div>
            <div className="detalhe-item">
              <strong>Critério:</strong> {item.criterio_julgamento}
            </div>
            <div className="detalhe-item">
              <strong>Economia:</strong> {item.economia_obtida}
            </div>
            {item.prazo_execucao && (
              <div className="detalhe-item">
                <strong>Prazo:</strong> {item.prazo_execucao}
              </div>
            )}
          </div>
        </div>

        {item.observacoes && (
          <div className="content-section">
            <h5>💭 Observações</h5>
            <p className="observacoes">{item.observacoes}</p>
          </div>
        )}
      </div>

      <div className="card-actions">
        <button className="action-btn primary">
          🔗 Ver Original
        </button>
        <button className="action-btn secondary">
          📋 Usar como Template
        </button>
        <button className="action-btn secondary">
          📊 Analisar Padrões
        </button>
      </div>
    </div>
  );

  return (
    <div className="base-conhecimento-container">
      <div className="conhecimento-header">
        <h1>🧠 Base de Conhecimento Inteligente</h1>
        <p>Aprenda com licitações bem-sucedidas e melhore seus editais</p>
      </div>

      <div className="conhecimento-tabs">
        <button 
          className={`tab-button ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          📊 Dashboard
        </button>
        <button 
          className={`tab-button ${activeTab === 'explorar' ? 'active' : ''}`}
          onClick={() => setActiveTab('explorar')}
        >
          🔍 Explorar Conhecimento
        </button>
        <button 
          className={`tab-button ${activeTab === 'padroes' ? 'active' : ''}`}
          onClick={() => setActiveTab('padroes')}
        >
          ⭐ Padrões de Sucesso
        </button>
      </div>

      {activeTab !== 'dashboard' && (
        <div className="search-filters">
          <div className="search-box">
            <input
              type="text"
              placeholder="🔍 Buscar na base de conhecimento..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          <div className="filter-box">
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
            >
              <option value="all">Todas as Categorias</option>
              <option value="servicos">Serviços</option>
              <option value="ti">Tecnologia da Informação</option>
              <option value="obras">Obras</option>
              <option value="bens">Bens</option>
              <option value="consultoria">Consultoria</option>
            </select>
          </div>
        </div>
      )}

      <div className="conhecimento-content">
        {activeTab === 'dashboard' && renderDashboard()}
        
        {activeTab === 'explorar' && (
          <div className="conhecimento-list">
            <div className="list-header">
              <h2>📚 Explorar Base de Conhecimento</h2>
              <p>Encontrados {filteredConhecimentos.length} documentos</p>
            </div>
            {filteredConhecimentos.map(renderConhecimentoCard)}
          </div>
        )}
        
        {activeTab === 'padroes' && (
          <div className="conhecimento-list">
            <div className="list-header">
              <h2>⭐ Padrões de Sucesso Identificados</h2>
              <p>Licitações com resultados excepcionais para usar como referência</p>
            </div>
            {filteredConhecimentos
              .filter(item => item.tipo === 'padrao_sucesso')
              .map(renderConhecimentoCard)}
          </div>
        )}
      </div>

      <div className="conhecimento-actions">
        <button className="action-button primary">
          🔄 Atualizar Base de Conhecimento
        </button>
        <button className="action-button secondary">
          📊 Gerar Relatório de Insights
        </button>
        <button className="action-button secondary">
          ⚙️ Configurar Coleta Automática
        </button>
      </div>
    </div>
  );
};

export default BaseConhecimento;
