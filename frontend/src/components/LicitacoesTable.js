import React, { useState } from 'react';
import './LicitacoesTable.css';
import { saveAs } from "file-saver";

// Componente de tabela para exibir licitações e modal de detalhes
function LicitacoesTable({ licitacoes }) {
  // Estados para modal, seleção e status de análise
  const [modalOpen, setModalOpen] = useState(false); // Controle do modal
  const [selected, setSelected] = useState(null); // Licitação selecionada
  const [loadingAnalise, setLoadingAnalise] = useState(false); // Status de geração de análise
  const [erroAnalise, setErroAnalise] = useState(null); // Erro na geração de análise
  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

  // Abre o modal de detalhes
  const openModal = (lic) => {
    setSelected(lic);
    setModalOpen(true);
  };
  // Fecha o modal
  const closeModal = () => {
    setModalOpen(false);
    setSelected(null);
  };

  // Chama o backend para gerar análise via IA
  const gerarAnalise = async (id) => {
    setLoadingAnalise(true);
    setErroAnalise(null);
    try {
      const resp = await fetch(`${API_URL}/gerar_analise?id=${encodeURIComponent(id)}`, { method: 'POST' });
      if (!resp.ok) throw new Error('Erro ao gerar análise');
      const data = await resp.json();
      setSelected(data);
    } catch (e) {
      setErroAnalise('Erro ao gerar análise.');
    } finally {
      setLoadingAnalise(false);
    }
  };

  // Exporta a análise da licitação selecionada em .txt
  function baixarAnalise(lic) {
    let txt = `Licitação: ${lic.id}\n`;
    txt += `Objeto: ${lic.objeto || '-'}\n`;
    txt += `Resumo: ${lic.resumo || '-'}\n`;
    txt += `Data de Abertura: ${lic.data_abertura || '-'}\n`;
    if (lic.risco_geral) txt += `Risco Geral: ${lic.risco_geral}\n`;
    if (lic.analise_juridica_texto) txt += `\n[Análise Jurídica]\n${lic.analise_juridica_texto}\n`;
    if (lic.pontos_de_atencao_juridica && lic.pontos_de_atencao_juridica.length > 0) {
      txt += `Pontos de Atenção Jurídica:\n`;
      lic.pontos_de_atencao_juridica.forEach((p, i) => txt += `  - ${p}\n`);
    }
    if (lic.analise_mercado_texto) txt += `\n[Análise de Mercado]\n${lic.analise_mercado_texto}\n`;
    if (lic.analise_cambial_texto) txt += `\n[Análise Cambial]\n${lic.analise_cambial_texto}\n`;
    if (lic.resumo_executivo_gerencial) txt += `\n[Resumo Executivo Gerencial]\n${lic.resumo_executivo_gerencial}\n`;
    if (lic.recomendacao_final) txt += `\n[Recomendação Final]\n${lic.recomendacao_final}\n`;
    const blob = new Blob([txt], { type: "text/plain;charset=utf-8" });
    saveAs(blob, `analise_${lic.id}.txt`);
  }

  // Renderização condicional para ausência de dados
  if (!licitacoes || licitacoes.length === 0) {
    return <p className="no-data-message">Nenhuma licitação encontrada.</p>;
  }
  // Renderização principal: tabela e modal
  return (
    <div className="licitacoes-table-container">
      <table className="licitacoes-table">
        <thead>
          <tr>
            <th className="objeto-col">Objeto</th>
            <th className="resumo-col">Resumo</th>
            <th>ID</th>
            <th>Data de Abertura</th>
          </tr>
        </thead>
        <tbody>
          {licitacoes.map((lic) => (
            <tr key={lic.id} className="licitacao-row" onClick={() => openModal(lic)} style={{cursor: 'pointer'}}>
              <td className="objeto-col">{lic.objeto || '-'}</td>
              <td className="resumo-col">{lic.resumo || '-'}</td>
              <td>{lic.id}</td>
              <td>{lic.data_abertura || '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {/* Modal de detalhes da licitação */}
      {modalOpen && selected && (
        <div className="licitacao-modal-overlay" onClick={closeModal}>
          <div className="licitacao-modal" onClick={e => e.stopPropagation()}>
            <button className="close-modal-btn" onClick={closeModal}>×</button>
            <h2>Detalhes da Licitação</h2>
            <div style={{marginBottom: 16, textAlign: 'center'}}>
              <button className="btn-gerar-analise" onClick={() => gerarAnalise(selected.id)} disabled={loadingAnalise}>
                {loadingAnalise ? 'Gerando Análise...' : 'Gerar Análise'}
              </button>
              {erroAnalise && <span style={{color:'#dc3545', marginLeft:10}}>{erroAnalise}</span>}
            </div>
            <div className="licitacao-modal-content">
              {/* Blocos de análise destacados */}
              {selected.risco_geral && (
                <div className={`modal-risco-geral risco-${(selected.risco_geral || '').toLowerCase()}`.replace(' ', '-') }>
                  <span className="risco-label-modal">Risco Geral:</span> {selected.risco_geral}
                </div>
              )}
              {selected.analise_juridica_texto && (
                <div className="modal-section modal-juridica">
                  <h3>Análise Jurídica</h3>
                  <p>{selected.analise_juridica_texto}</p>
                  {selected.pontos_de_atencao_juridica && selected.pontos_de_atencao_juridica.length > 0 && (
                    <div className="pontos-atencao-modal">
                      <h4>⚠️ Pontos de Atenção Jurídica:</h4>
                      <ul>
                        {selected.pontos_de_atencao_juridica.map((ponto, idx) => (
                          <li key={idx}>{ponto}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
              {/* Campos principais */}
              <p><strong>Objeto:</strong> {selected.objeto}</p>
              <p><strong>Resumo:</strong> {selected.resumo}</p>
              <p><strong>ID:</strong> {selected.id}</p>
              <p><strong>Data de Abertura:</strong> {selected.data_abertura}</p>
              {/* Outras análises */}
              {selected.analise_mercado_texto && (
                <div className="modal-section">
                  <h3>Análise de Mercado</h3>
                  <p>{selected.analise_mercado_texto}</p>
                </div>
              )}
              {selected.analise_cambial_texto && (
                <div className="modal-section">
                  <h3>Análise Cambial</h3>
                  <p>{selected.analise_cambial_texto}</p>
                </div>
              )}
              {selected.resumo_executivo_gerencial && (
                <div className="modal-section">
                  <h3>Resumo Executivo Gerencial</h3>
                  <p>{selected.resumo_executivo_gerencial}</p>
                </div>
              )}
              {selected.recomendacao_final && (
                <div className="modal-section">
                  <h3>Recomendação Final</h3>
                  <p>{selected.recomendacao_final}</p>
                </div>
              )}
            </div>
            <div style={{marginTop: 18, textAlign: 'right'}}>
              <button className="btn-download-analise" onClick={() => baixarAnalise(selected)}>
                Baixar Análise
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default LicitacoesTable; 