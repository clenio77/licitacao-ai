import React, { useState, useEffect } from 'react';
import './Feedback.css';

const Feedback = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [feedbackData, setFeedbackData] = useState({
    setor: [],
    empresa: [],
    licitacao: []
  });
  const [analytics, setAnalytics] = useState({
    satisfacao_geral: 0,
    total_respostas: 0,
    problemas_identificados: 0,
    melhorias_implementadas: 0
  });
  const [loading, setLoading] = useState(false);

  // Simular dados de feedback
  useEffect(() => {
    const mockData = {
      setor: [
        {
          id: 1,
          edital_id: 'ED-2024-001',
          setor_nome: 'Gerência de Facilities',
          responsavel_nome: 'João Silva',
          facilidade_uso: 4,
          qualidade_edital: 4,
          adequacao_requisitos: 5,
          pontos_positivos: 'Sistema muito rápido e intuitivo',
          pontos_negativos: 'Algumas especificações ficaram genéricas',
          data_feedback: '2024-01-15'
        },
        {
          id: 2,
          edital_id: 'ED-2024-002',
          setor_nome: 'TI Corporativa',
          responsavel_nome: 'Maria Santos',
          facilidade_uso: 5,
          qualidade_edital: 4,
          adequacao_requisitos: 4,
          pontos_positivos: 'Interface excelente, processo claro',
          pontos_negativos: 'Poderia ter mais templates para TI',
          data_feedback: '2024-01-16'
        }
      ],
      empresa: [
        {
          id: 1,
          edital_id: 'ED-2024-001',
          empresa_nome: 'Limpeza Total Ltda',
          clareza_objeto: 4,
          adequacao_especificacoes: 3,
          criterios_julgamento: 5,
          aspectos_positivos: 'Edital claro e bem estruturado',
          aspectos_negativos: 'Especificações muito restritivas',
          data_feedback: '2024-01-17'
        }
      ],
      licitacao: [
        {
          id: 1,
          edital_id: 'ED-2024-001',
          avaliador_nome: 'Carlos Pregoeiro',
          qualidade_tecnica: 4,
          conformidade_legal: 5,
          adequacao_modalidade: 5,
          pontos_fortes: 'Edital bem estruturado, documentação completa',
          areas_melhoria: 'Melhorar especificações técnicas',
          data_feedback: '2024-01-18'
        }
      ]
    };

    setFeedbackData(mockData);
    setAnalytics({
      satisfacao_geral: 4.1,
      total_respostas: 4,
      problemas_identificados: 3,
      melhorias_implementadas: 2
    });
  }, []);

  const renderDashboard = () => (
    <div className="feedback-dashboard">
      <div className="analytics-cards">
        <div className="analytics-card">
          <div className="card-icon">📊</div>
          <div className="card-content">
            <h3>Satisfação Geral</h3>
            <div className="metric-value">{analytics.satisfacao_geral}/5</div>
            <div className="metric-label">Média de todas as avaliações</div>
          </div>
        </div>

        <div className="analytics-card">
          <div className="card-icon">💬</div>
          <div className="card-content">
            <h3>Total de Respostas</h3>
            <div className="metric-value">{analytics.total_respostas}</div>
            <div className="metric-label">Feedbacks recebidos</div>
          </div>
        </div>

        <div className="analytics-card">
          <div className="card-icon">⚠️</div>
          <div className="card-content">
            <h3>Problemas Identificados</h3>
            <div className="metric-value">{analytics.problemas_identificados}</div>
            <div className="metric-label">Requerem atenção</div>
          </div>
        </div>

        <div className="analytics-card">
          <div className="card-icon">✅</div>
          <div className="card-content">
            <h3>Melhorias Implementadas</h3>
            <div className="metric-value">{analytics.melhorias_implementadas}</div>
            <div className="metric-label">Baseadas em feedback</div>
          </div>
        </div>
      </div>

      <div className="feedback-charts">
        <div className="chart-container">
          <h3>Satisfação por Stakeholder</h3>
          <div className="satisfaction-bars">
            <div className="satisfaction-bar">
              <span className="bar-label">Setores Requisitantes</span>
              <div className="bar-track">
                <div className="bar-fill" style={{width: '82%'}}></div>
              </div>
              <span className="bar-value">4.1/5</span>
            </div>
            <div className="satisfaction-bar">
              <span className="bar-label">Empresas Licitantes</span>
              <div className="bar-track">
                <div className="bar-fill" style={{width: '76%'}}></div>
              </div>
              <span className="bar-value">3.8/5</span>
            </div>
            <div className="satisfaction-bar">
              <span className="bar-label">Setor de Licitação</span>
              <div className="bar-track">
                <div className="bar-fill" style={{width: '86%'}}></div>
              </div>
              <span className="bar-value">4.3/5</span>
            </div>
          </div>
        </div>

        <div className="chart-container">
          <h3>Principais Problemas Identificados</h3>
          <div className="problems-list">
            <div className="problem-item">
              <span className="problem-icon">🔧</span>
              <div className="problem-content">
                <div className="problem-title">Especificações muito genéricas</div>
                <div className="problem-count">2 ocorrências</div>
              </div>
            </div>
            <div className="problem-item">
              <span className="problem-icon">📋</span>
              <div className="problem-content">
                <div className="problem-title">Falta de templates específicos</div>
                <div className="problem-count">1 ocorrência</div>
              </div>
            </div>
            <div className="problem-item">
              <span className="problem-icon">⚖️</span>
              <div className="problem-content">
                <div className="problem-title">Critérios muito restritivos</div>
                <div className="problem-count">1 ocorrência</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderFeedbackList = (type) => {
    const data = feedbackData[type] || [];
    
    return (
      <div className="feedback-list">
        {data.map(item => (
          <div key={item.id} className="feedback-item">
            <div className="feedback-header">
              <h4>{item.setor_nome || item.empresa_nome || item.avaliador_nome}</h4>
              <span className="feedback-date">{item.data_feedback}</span>
            </div>
            
            <div className="feedback-ratings">
              {type === 'setor' && (
                <>
                  <div className="rating-item">
                    <span>Facilidade de Uso:</span>
                    <div className="stars">{'★'.repeat(item.facilidade_uso)}{'☆'.repeat(5-item.facilidade_uso)}</div>
                  </div>
                  <div className="rating-item">
                    <span>Qualidade do Edital:</span>
                    <div className="stars">{'★'.repeat(item.qualidade_edital)}{'☆'.repeat(5-item.qualidade_edital)}</div>
                  </div>
                </>
              )}
              
              {type === 'empresa' && (
                <>
                  <div className="rating-item">
                    <span>Clareza do Objeto:</span>
                    <div className="stars">{'★'.repeat(item.clareza_objeto)}{'☆'.repeat(5-item.clareza_objeto)}</div>
                  </div>
                  <div className="rating-item">
                    <span>Critérios de Julgamento:</span>
                    <div className="stars">{'★'.repeat(item.criterios_julgamento)}{'☆'.repeat(5-item.criterios_julgamento)}</div>
                  </div>
                </>
              )}
              
              {type === 'licitacao' && (
                <>
                  <div className="rating-item">
                    <span>Qualidade Técnica:</span>
                    <div className="stars">{'★'.repeat(item.qualidade_tecnica)}{'☆'.repeat(5-item.qualidade_tecnica)}</div>
                  </div>
                  <div className="rating-item">
                    <span>Conformidade Legal:</span>
                    <div className="stars">{'★'.repeat(item.conformidade_legal)}{'☆'.repeat(5-item.conformidade_legal)}</div>
                  </div>
                </>
              )}
            </div>
            
            <div className="feedback-comments">
              <div className="comment-section">
                <strong>Pontos Positivos:</strong>
                <p>{item.pontos_positivos || item.aspectos_positivos || item.pontos_fortes}</p>
              </div>
              <div className="comment-section">
                <strong>Pontos Negativos:</strong>
                <p>{item.pontos_negativos || item.aspectos_negativos || item.areas_melhoria}</p>
              </div>
            </div>
          </div>
        ))}
        
        {data.length === 0 && (
          <div className="no-feedback">
            <p>Nenhum feedback disponível para este stakeholder.</p>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="feedback-container">
      <div className="feedback-header">
        <h1>💬 Sistema de Feedback e Melhoria Contínua</h1>
        <p>Coletando opiniões de todos os stakeholders para melhorar continuamente o sistema</p>
      </div>

      <div className="feedback-tabs">
        <button 
          className={`tab-button ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          📊 Dashboard
        </button>
        <button 
          className={`tab-button ${activeTab === 'setor' ? 'active' : ''}`}
          onClick={() => setActiveTab('setor')}
        >
          📋 Setores Requisitantes
        </button>
        <button 
          className={`tab-button ${activeTab === 'empresa' ? 'active' : ''}`}
          onClick={() => setActiveTab('empresa')}
        >
          🏢 Empresas Licitantes
        </button>
        <button 
          className={`tab-button ${activeTab === 'licitacao' ? 'active' : ''}`}
          onClick={() => setActiveTab('licitacao')}
        >
          ⚖️ Setor de Licitação
        </button>
      </div>

      <div className="feedback-content">
        {activeTab === 'dashboard' && renderDashboard()}
        {activeTab === 'setor' && (
          <div>
            <h2>Feedback dos Setores Requisitantes</h2>
            <p>Avaliações sobre usabilidade, qualidade dos editais e adequação aos requisitos.</p>
            {renderFeedbackList('setor')}
          </div>
        )}
        {activeTab === 'empresa' && (
          <div>
            <h2>Feedback das Empresas Licitantes</h2>
            <p>Avaliações sobre clareza, competitividade e especificações técnicas dos editais.</p>
            {renderFeedbackList('empresa')}
          </div>
        )}
        {activeTab === 'licitacao' && (
          <div>
            <h2>Feedback do Setor de Licitação</h2>
            <p>Avaliações técnicas sobre conformidade legal, qualidade e eficiência do processo.</p>
            {renderFeedbackList('licitacao')}
          </div>
        )}
      </div>

      <div className="feedback-actions">
        <button className="action-button primary">
          📧 Enviar Solicitação de Feedback
        </button>
        <button className="action-button secondary">
          📊 Gerar Relatório de Impacto
        </button>
        <button className="action-button secondary">
          🔧 Configurar Automação
        </button>
      </div>
    </div>
  );
};

export default Feedback;
