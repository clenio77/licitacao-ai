import React from 'react';
import './LicitacaoCard.css';

// Componente de card para exibir detalhes resumidos de uma licitação
function LicitacaoCard({ licitacao }) {
  // Flags para exibir seções de acordo com os dados disponíveis
  const hasJuridicalAttention = licitacao.pontos_de_atencao_juridica && licitacao.pontos_de_atencao_juridica.length > 0;
  const hasMarketAnalysis = licitacao.analise_mercado_texto;
  const hasManagerialSummary = licitacao.resumo_executivo_gerencial;
  const hasRiskNotificationEmail = licitacao.ultima_notificacao_risco;
  const hasRiskNotificationTeams = licitacao.ultima_notificacao_teams_risco;
  const hasCurrencyAnalysis = licitacao.analise_cambial_texto;
  const hasCurrencyNotification = licitacao.ultima_notificacao_variacao_cambial;

  // Função auxiliar para definir classe CSS do risco
  const getRiskClass = (risk) => {
    switch (risk?.toLowerCase()) {
      case 'alto': return 'risk-high';
      case 'médio': return 'risk-medium';
      case 'baixo': return 'risk-low';
      default: return '';
    }
  };

  // Renderização principal do card
  return (
    <div className={`licitacao-card ${hasJuridicalAttention ? 'attention-card' : ''}`}>
      <div className="objeto-destaque">{licitacao.objeto || 'Objeto Não Informado'}</div>
      <ul className="licitacao-info-list">
        {/* Campos principais da licitação */}
        <li><strong>Modalidade:</strong> {licitacao.modalidade || 'N/A'}</li>
        <li><strong>Número do Edital:</strong> {licitacao.numero_edital || 'N/A'}</li>
        <li><strong>Data de Publicação:</strong> {licitacao.data_publicacao || 'N/A'}</li>
        <li><strong>UASG:</strong> {licitacao.uasg || 'N/A'}</li>
        <li><strong>Dependência:</strong> {licitacao.dependencia || 'N/A'}</li>
        <li><strong>UF:</strong> {licitacao.uf || 'N/A'}</li>
        <li><strong>Quantidade de Itens:</strong> {licitacao.quantidade_itens || 'N/A'}</li>
        <li><strong>NUP:</strong> {licitacao.nup || 'N/A'}</li>
        <li><strong>ID:</strong> {licitacao.id}</li>
        <li><strong>Data de Abertura:</strong> {licitacao.data_abertura || 'N/A'}</li>
        <li><strong>Prazo Proposta:</strong> {licitacao.prazo_proposta || 'N/A'}</li>
        <li><strong>Valor Estimado:</strong> {licitacao.valor_estimado ? `R$ ${licitacao.valor_estimado.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : 'Não Informado'}</li>
        <li><strong>Requisito Principal:</strong> {licitacao.requisito_habilitacao_principal || 'N/A'}</li>
      </ul>
      <p className="licitacao-resumo"><strong>Resumo:</strong> {licitacao.resumo || 'N/A'}</p>

      {/* Seção de Análise Jurídica */}
      {licitacao.analise_juridica_texto && (
        <div className="licitacao-juridica">
          <h3>Análise Jurídica</h3>
          <p>{licitacao.analise_juridica_texto}</p>
          {hasJuridicalAttention && (
            <div className="pontos-atencao">
              <h4>⚠️ Pontos de Atenção Jurídica:</h4>
              <ul>
                {licitacao.pontos_de_atencao_juridica.map((ponto, index) => (
                  <li key={index}>{ponto}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {/* Seção de Análise de Mercado */}
      {hasMarketAnalysis && (
        <div className="licitacao-mercado">
          <h3>Análise de Mercado</h3>
          <p>{licitacao.analise_mercado_texto}</p>
          {licitacao.sugestao_preco_referencia !== null && (
            <p><strong>Sugestão de Preço Referência:</strong> {typeof licitacao.sugestao_preco_referencia === 'number' ? `R$ ${licitacao.sugestao_preco_referencia.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : licitacao.sugestao_preco_referencia}</p>
          )}
          {hasCurrencyAnalysis && (
            <p className="currency-analysis"><strong>Análise Cambial:</strong> {licitacao.analise_cambial_texto}</p>
          )}
        </div>
      )}

      {/* Seção de Gerenciamento */}
      {hasManagerialSummary && (
        <div className="licitacao-gerencial">
          <h3>Análise Gerencial</h3>
          <p><strong>Resumo Executivo:</strong> {licitacao.resumo_executivo_gerencial}</p>
          <p>
            <strong>Risco Geral:</strong>{' '}
            <span className={`risk-label ${getRiskClass(licitacao.risco_geral)}`}>
              {licitacao.risco_geral || 'N/A'}
            </span>
          </p>
          <p><strong>Recomendação Final:</strong> {licitacao.recomendacao_final || 'N/A'}</p>
          {hasRiskNotificationEmail && (
            <p className="notification-status">
              📧 Último Alerta de Risco (Email): {new Date(licitacao.ultima_notificacao_risco).toLocaleString('pt-BR')}
            </p>
          )}
          {hasRiskNotificationTeams && (
            <p className="notification-status teams-status">
              💬 Último Alerta de Risco (Teams): {new Date(licitacao.ultima_notificacao_teams_risco).toLocaleString('pt-BR')}
            </p>
          )}
          {hasCurrencyNotification && (
            <p className="notification-status currency-status">
              📈 Último Alerta Cambial: {new Date(licitacao.ultima_notificacao_variacao_cambial).toLocaleString('pt-BR')}
            </p>
          )}
        </div>
      )}

      {/* Link para o edital original */}
      {licitacao.link_original && (
        <a href={licitacao.link_original} target="_blank" rel="noopener noreferrer" className="licitacao-link">
          Ver Edital Original
        </a>
      )}
    </div>
  );
}

export default LicitacaoCard;