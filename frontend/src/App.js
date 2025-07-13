import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import LicitacaoCard from './components/LicitacaoCard';
import LicitacoesTable from './components/LicitacoesTable';
import GerarEdital from './pages/GerarEdital';
import BaseConhecimento from './pages/BaseConhecimento';
import Feedback from './pages/Feedback';
import NovaRequisicao from './pages/NovaRequisicao';
import './App.css';

// Componente para a página de análise de licitações (página original)
function LicitacoesAnalise() {
  // Estados para controle de dados, filtros, busca manual e status
  const [licitacoes, setLicitacoes] = useState([]); // Lista de licitações carregadas da API
  const [loading, setLoading] = useState(true); // Status de carregamento
  const [error, setError] = useState(null); // Mensagem de erro
  const [searchTerm, setSearchTerm] = useState(''); // Termo de busca
  const [filterStatus, setFilterStatus] = useState('todos'); // Filtro de status
  const [manualSearchUrl, setManualSearchUrl] = useState('http://comprasnet.gov.br/acesso.asp?url=/ConsultaLicitacoes/ConsLicitacao_Filtro.asp');
  const [manualSearchTerm, setManualSearchTerm] = useState('');
  const [manualStartDate, setManualStartDate] = useState('');
  const [manualEndDate, setManualEndDate] = useState('');
  const [manualModalidade, setManualModalidade] = useState('');
  const [manualOrgao, setManualOrgao] = useState('');
  const [manualValorMin, setManualValorMin] = useState('');
  const [manualValorMax, setManualValorMax] = useState('');
  const [manualPortal, setManualPortal] = useState('comprasnet');
  const [manualResults, setManualResults] = useState([]);
  const [manualLoading, setManualLoading] = useState(false);
  const [manualError, setManualError] = useState(null);

  const API_URL = process.env.REACT_APP_API_URL;

  // Função para buscar licitações do backend
  const fetchLicitacoes = async () => {
    try {
      const response = await fetch(API_URL + '/licitacoes/');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setLicitacoes(data);
    } catch (e) {
      setError(`Não foi possível carregar os dados das licitações. Verifique se o servidor FastAPI está rodando em http://localhost:8000. Erro: ${e.message}`);
      console.error("Erro ao carregar licitações:", e);
    } finally {
      setLoading(false);
    }
  };

  // useEffect para buscar licitações ao montar e atualizar periodicamente
  useEffect(() => {
    fetchLicitacoes();
    const intervalId = setInterval(fetchLicitacoes, 15000); // Atualiza a cada 15 segundos
    return () => clearInterval(intervalId); // Limpa o intervalo ao desmontar
  }, []);

  // Filtro local das licitações conforme busca e status
  const filteredLicitacoes = licitacoes.filter(licitacao => {
    const matchesSearch = searchTerm === '' ||
      licitacao.objeto.toLowerCase().includes(searchTerm.toLowerCase()) ||
      licitacao.resumo.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (licitacao.analise_juridica_texto && licitacao.analise_juridica_texto.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (licitacao.analise_mercado_texto && licitacao.analise_mercado_texto.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (licitacao.resumo_executivo_gerencial && licitacao.resumo_executivo_gerencial.toLowerCase().includes(searchTerm.toLowerCase()));

    const hasJuridicalAttention = licitacao.pontos_de_atencao_juridica && licitacao.pontos_de_atencao_juridica.length > 0;
    const isHighOrMediumRisk = licitacao.risco_geral && (licitacao.risco_geral.toLowerCase() === 'alto' || licitacao.risco_geral.toLowerCase() === 'médio');
    
    const matchesStatus = filterStatus === 'todos' ||
      (filterStatus === 'com_atencao_juridica' && hasJuridicalAttention) ||
      (filterStatus === 'com_risco' && isHighOrMediumRisk) ||
      (filterStatus === 'sem_risco' && !isHighOrMediumRisk); 
      // Adicione mais filtros conforme os status que você quer gerenciar.
      // Para o MVP, 'sem_risco' e 'com_risco' podem usar 'risco_geral'.

    return matchesSearch && matchesStatus;
  });

  // Função para busca manual de licitações dos Correios
  const handleManualSearch = async () => {
    setManualLoading(true);
    setManualError(null);
    setManualResults([]);
    try {
      const body = {
        data_inicial: manualStartDate,
        data_final: manualEndDate
        // Se quiser filtrar por assunto no futuro, adicione: termo_assunto: manualSearchTerm
      };
      const response = await fetch(API_URL + '/forcar_busca_licitacoes/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setManualResults(data.licitacoes || []);
    } catch (e) {
      setManualError('Erro ao buscar licitações manualmente: ' + e.message);
    } finally {
      setManualLoading(false);
    }
  };

  // Renderização condicional para loading e erro
  if (loading) {
    return <div className="loading-message">Carregando licitações...</div>;
  }
  if (error) {
    return <div className="error-message">Erro: {error}</div>;
  }

  // Contadores para KPIs simples
  const totalLicitacoes = licitacoes.length;
  const licitacoesComAtencaoJuridica = licitacoes.filter(l => l.pontos_de_atencao_juridica && l.pontos_de_atencao_juridica.length > 0).length;
  const licitacoesComRiscoAltoOuMedio = licitacoes.filter(l => l.risco_geral && (l.risco_geral.toLowerCase() === 'alto' || l.risco_geral.toLowerCase() === 'médio')).length;

  // JSX principal da página de análise
  return (
    <div className="App">
      {/* Cabeçalho do site */}
      <header className="App-header">
        <h1>📊 Análise de Licitações dos Correios</h1>
        <p>Dados processados automaticamente por Agentes Inteligentes</p>
        <nav className="header-nav">
          <Link to="/" className="nav-link">📊 Análise</Link>
          <Link to="/nova-requisicao" className="nav-link">📝 Nova Requisição</Link>
          <Link to="/gerar-edital" className="nav-link">� Gerar Edital</Link>
          <Link to="/base-conhecimento" className="nav-link">🧠 Base de Conhecimento</Link>
          <Link to="/feedback" className="nav-link">💬 Feedback</Link>
        </nav>
      </header>
      <main className="main-content">
        {/* KPIs */}
        <section className="kpi-section">
          <div className="kpi-card">
            <h3>Total de Licitações</h3>
            <p>{totalLicitacoes}</p>
          </div>
          <div className="kpi-card attention">
            <h3>Com Atenção Jurídica</h3>
            <p>{licitacoesComAtencaoJuridica}</p>
          </div>
          <div className="kpi-card attention"> {/* Pode ter uma classe diferente para risco */}
            <h3>Com Risco (Médio/Alto)</h3>
            <p>{licitacoesComRiscoAltoOuMedio}</p>
          </div>
        </section>
        {/* Filtros de busca e status */}
        <section className="filters-section">
          <input
            type="text"
            placeholder="Buscar por objeto, resumo ou análise..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="status-filter"
          >
            <option value="todos">Todos os Status</option>
            <option value="sem_risco">Apenas Baixo Risco</option>
            <option value="com_risco">Com Risco (Médio/Alto)</option>
            <option value="com_atencao_juridica">Com Atenção Jurídica</option>
          </select>
        </section>
        {/* Busca manual de licitações */}
        <section className="manual-search-section">
          <h3>Busca Manual de Licitações dos Correios</h3>
          <form
            className="manual-search-form"
            onSubmit={e => { e.preventDefault(); handleManualSearch(); }}
          >
            {/* Portal e URL ocultos removidos, pois não são mais usados */}
            <input
              type="text"
              value={manualSearchTerm}
              onChange={e => setManualSearchTerm(e.target.value)}
              placeholder="Ex: TI, engenharia, serviços... (deixe em branco para todas)"
            />
            <input
              type="date"
              value={manualStartDate}
              onChange={e => setManualStartDate(e.target.value)}
              placeholder="Data inicial"
            />
            <input
              type="date"
              value={manualEndDate}
              onChange={e => setManualEndDate(e.target.value)}
              placeholder="Data final"
            />
            <button type="submit" disabled={manualLoading}>
              {manualLoading ? 'Buscando...' : 'Buscar Licitações dos Correios'}
            </button>
          </form>
          <div style={{ fontSize: '0.95em', color: '#555', marginTop: 8 }}>
            Deixe o campo em branco para buscar todas as áreas dos Correios, ou preencha para filtrar por área específica.
          </div>
          {manualError && <div className="error-message">{manualError}</div>}
          {manualResults.length > 0 && (
            <div className="manual-results-list">
              <h4>Resultados da Busca Manual:</h4>
              <ul>
                {manualResults.map((lic, idx) => (
                  <li key={lic.id || idx}>
                    <a href={lic.url} target="_blank" rel="noopener noreferrer">{lic.url}</a>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </section>
        {/* Listagem de licitações em tabela */}
        <section className="licitacoes-list">
          {filteredLicitacoes.length > 0 ? (
            <LicitacoesTable licitacoes={filteredLicitacoes} />
          ) : (
            <p className="no-data-message">Nenhum edital corresponde aos critérios de filtro/busca.</p>
          )}
        </section>
      </main>
      {/* Rodapé */}
      <footer className="App-footer">
        <p>Desenvolvido com CrewAI, Playwright, PostgreSQL e React</p>
      </footer>
    </div>
  );
}

// Componente principal da aplicação com roteamento
function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<LicitacoesAnalise />} />
          <Route path="/nova-requisicao" element={<NovaRequisicao />} />
          <Route path="/gerar-edital" element={<GerarEdital />} />
          <Route path="/base-conhecimento" element={<BaseConhecimento />} />
          <Route path="/feedback" element={<Feedback />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;