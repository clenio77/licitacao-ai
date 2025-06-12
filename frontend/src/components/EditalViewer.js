import React, { useState } from 'react';
import './EditalViewer.css';

function EditalViewer({ edital, onEdit, onReset }) {
  const [activeTab, setActiveTab] = useState('conteudo');
  const [showAnalises, setShowAnalises] = useState(false);

  const downloadEdital = () => {
    const element = document.createElement('a');
    const file = new Blob([edital.conteudo_edital], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = `edital_${edital.id}.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(edital.conteudo_edital).then(() => {
      alert('Conteúdo copiado para a área de transferência!');
    });
  };

  const getRiscoColor = (risco) => {
    switch (risco?.toLowerCase()) {
      case 'baixo': return '#28a745';
      case 'medio': return '#ffc107';
      case 'alto': return '#fd7e14';
      case 'critico': return '#dc3545';
      default: return '#6c757d';
    }
  };

  const getRiscoIcon = (risco) => {
    switch (risco?.toLowerCase()) {
      case 'baixo': return '✅';
      case 'medio': return '⚠️';
      case 'alto': return '🔶';
      case 'critico': return '🚨';
      default: return '❓';
    }
  };

  return (
    <div className="edital-viewer">
      {/* Header com informações básicas */}
      <div className="viewer-header">
        <div className="header-info">
          <h3>📄 {edital.solicitacao_original?.objeto || 'Edital Gerado'}</h3>
          <div className="header-meta">
            <span className="meta-item">
              <strong>ID:</strong> {edital.id}
            </span>
            <span className="meta-item">
              <strong>Status:</strong> 
              <span className={`status-badge status-${edital.status}`}>
                {edital.status}
              </span>
            </span>
            <span className="meta-item">
              <strong>Gerado em:</strong> {new Date(edital.data_criacao).toLocaleString('pt-BR')}
            </span>
          </div>
        </div>

        <div className="header-actions">
          <button onClick={copyToClipboard} className="btn btn-secondary btn-sm">
            📋 Copiar
          </button>
          <button onClick={downloadEdital} className="btn btn-secondary btn-sm">
            💾 Download
          </button>
          <button onClick={onEdit} className="btn btn-primary btn-sm">
            ✏️ Editar
          </button>
        </div>
      </div>

      {/* Análise de Risco Resumida */}
      {edital.analise_risco && (
        <div className="risk-summary">
          <div className="risk-indicator">
            <span className="risk-icon">
              {getRiscoIcon(edital.analise_risco.risco_geral)}
            </span>
            <div className="risk-info">
              <span className="risk-label">Risco Geral:</span>
              <span 
                className="risk-value"
                style={{ color: getRiscoColor(edital.analise_risco.risco_geral) }}
              >
                {edital.analise_risco.risco_geral?.toUpperCase() || 'N/A'}
              </span>
            </div>
          </div>
          
          {edital.analise_risco.probabilidade_sucesso && (
            <div className="success-probability">
              <span className="prob-label">Probabilidade de Sucesso:</span>
              <span className="prob-value">
                {Math.round(edital.analise_risco.probabilidade_sucesso * 100)}%
              </span>
            </div>
          )}

          <button 
            onClick={() => setShowAnalises(!showAnalises)}
            className="btn btn-link btn-sm"
          >
            {showAnalises ? 'Ocultar' : 'Ver'} Análises Detalhadas
          </button>
        </div>
      )}

      {/* Análises Detalhadas (colapsível) */}
      {showAnalises && (
        <div className="detailed-analyses">
          <div className="analyses-grid">
            {/* Análise Jurídica */}
            {edital.analise_juridica && (
              <div className="analysis-card juridica">
                <h4>⚖️ Análise Jurídica</h4>
                <div className="analysis-content">
                  <div className="analysis-status">
                    <span className={`status-indicator ${edital.analise_juridica.conforme ? 'success' : 'warning'}`}>
                      {edital.analise_juridica.conforme ? '✅ Conforme' : '⚠️ Atenção'}
                    </span>
                  </div>
                  {edital.analise_juridica.pontos_atencao?.length > 0 && (
                    <div className="points-list">
                      <strong>Pontos de Atenção:</strong>
                      <ul>
                        {edital.analise_juridica.pontos_atencao.map((ponto, index) => (
                          <li key={index}>{ponto}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Análise Técnica */}
            {edital.analise_tecnica && (
              <div className="analysis-card tecnica">
                <h4>🔧 Análise Técnica</h4>
                <div className="analysis-content">
                  <div className="analysis-status">
                    <span className={`status-indicator ${edital.analise_tecnica.viabilidade ? 'success' : 'warning'}`}>
                      {edital.analise_tecnica.viabilidade ? '✅ Viável' : '⚠️ Revisar'}
                    </span>
                  </div>
                  {edital.analise_tecnica.pontos_atencao?.length > 0 && (
                    <div className="points-list">
                      <strong>Pontos de Atenção:</strong>
                      <ul>
                        {edital.analise_tecnica.pontos_atencao.map((ponto, index) => (
                          <li key={index}>{ponto}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Análise Financeira */}
            {edital.analise_financeira && (
              <div className="analysis-card financeira">
                <h4>💰 Análise Financeira</h4>
                <div className="analysis-content">
                  <div className="analysis-status">
                    <span className={`status-indicator ${edital.analise_financeira.orcamento_adequado ? 'success' : 'warning'}`}>
                      {edital.analise_financeira.orcamento_adequado ? '✅ Adequado' : '⚠️ Revisar'}
                    </span>
                  </div>
                  {edital.analise_financeira.valor_sugerido && (
                    <div className="financial-info">
                      <strong>Valor Sugerido:</strong> R$ {edital.analise_financeira.valor_sugerido.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tabs para conteúdo */}
      <div className="content-tabs">
        <div className="tab-headers">
          <button 
            className={`tab-header ${activeTab === 'conteudo' ? 'active' : ''}`}
            onClick={() => setActiveTab('conteudo')}
          >
            📄 Conteúdo do Edital
          </button>
          <button 
            className={`tab-header ${activeTab === 'dados' ? 'active' : ''}`}
            onClick={() => setActiveTab('dados')}
          >
            📊 Dados da Solicitação
          </button>
          <button 
            className={`tab-header ${activeTab === 'melhorias' ? 'active' : ''}`}
            onClick={() => setActiveTab('melhorias')}
          >
            🔧 Melhorias Aplicadas
          </button>
        </div>

        <div className="tab-content">
          {activeTab === 'conteudo' && (
            <div className="content-panel">
              <div className="edital-content">
                <pre>{edital.conteudo_edital}</pre>
              </div>
            </div>
          )}

          {activeTab === 'dados' && (
            <div className="content-panel">
              <div className="data-grid">
                <div className="data-section">
                  <h4>📋 Dados Básicos</h4>
                  <div className="data-item">
                    <strong>Objeto:</strong> {edital.solicitacao_original?.objeto}
                  </div>
                  <div className="data-item">
                    <strong>Tipo:</strong> {edital.solicitacao_original?.tipo_licitacao}
                  </div>
                  <div className="data-item">
                    <strong>Categoria:</strong> {edital.solicitacao_original?.categoria}
                  </div>
                  <div className="data-item">
                    <strong>Valor Estimado:</strong> R$ {edital.solicitacao_original?.valor_total_estimado?.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                  </div>
                </div>

                <div className="data-section">
                  <h4>🏢 Setor Requisitante</h4>
                  <div className="data-item">
                    <strong>Nome:</strong> {edital.solicitacao_original?.setor_requisitante?.nome}
                  </div>
                  <div className="data-item">
                    <strong>Responsável:</strong> {edital.solicitacao_original?.setor_requisitante?.responsavel}
                  </div>
                  <div className="data-item">
                    <strong>Email:</strong> {edital.solicitacao_original?.setor_requisitante?.email}
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'melhorias' && (
            <div className="content-panel">
              <div className="improvements-list">
                {edital.melhorias_aplicadas?.length > 0 ? (
                  <ul>
                    {edital.melhorias_aplicadas.map((melhoria, index) => (
                      <li key={index} className="improvement-item">
                        <span className="improvement-icon">✨</span>
                        {melhoria}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <div className="empty-state">
                    <p>Nenhuma melhoria específica foi aplicada.</p>
                    <p className="help-text">O edital foi gerado seguindo as melhores práticas padrão.</p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Footer com ações */}
      <div className="viewer-footer">
        <div className="footer-info">
          <p>Edital gerado automaticamente pelo Sistema de Licitações dos Correios</p>
          <p>Baseado na Lei 14.133/2021 e melhores práticas identificadas</p>
        </div>
        
        <div className="footer-actions">
          <button onClick={onReset} className="btn btn-secondary">
            🆕 Gerar Novo Edital
          </button>
          <button onClick={onEdit} className="btn btn-primary">
            ✏️ Editar Este Edital
          </button>
        </div>
      </div>
    </div>
  );
}

export default EditalViewer;
