import React, { useState } from 'react';
import './GerarEdital.css';

const GerarEdital = () => {
  const [formData, setFormData] = useState({
    objeto: '',
    categoria: 'servicos',
    modalidade: 'pregao',
    valor_estimado: '',
    prazo_entrega: '',
    local_entrega: '',
    criterio_julgamento: 'menor_preco',
    exige_visita_tecnica: false,
    permite_consorcio: false,
    especificacoes_tecnicas: '',
    observacoes: ''
  });

  const [loading, setLoading] = useState(false);
  const [editalGerado, setEditalGerado] = useState(null);
  const [error, setError] = useState(null);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Simular geração de edital (em produção, seria uma chamada para a API)
      await new Promise(resolve => setTimeout(resolve, 3000)); // Simular processamento

      const editalMock = {
        id: 'ED-2024-' + Math.floor(Math.random() * 1000).toString().padStart(3, '0'),
        objeto: formData.objeto,
        categoria: formData.categoria,
        modalidade: formData.modalidade,
        valor_estimado: formData.valor_estimado,
        data_geracao: new Date().toLocaleDateString('pt-BR'),
        status: 'Gerado',
        conteudo: `
EDITAL DE LICITAÇÃO Nº ${Math.floor(Math.random() * 1000)}/2024

OBJETO: ${formData.objeto}

1. DISPOSIÇÕES PRELIMINARES
A Empresa Brasileira de Correios e Telégrafos - ECT, por meio de sua Gerência de Licitações, torna público que realizará licitação na modalidade ${formData.modalidade.toUpperCase()}, do tipo ${formData.criterio_julgamento.replace('_', ' ')}, para contratação de ${formData.objeto.toLowerCase()}.

2. DO OBJETO
2.1. O objeto desta licitação é a contratação de ${formData.objeto.toLowerCase()}, conforme especificações técnicas constantes no Anexo I deste Edital.

3. ESPECIFICAÇÕES TÉCNICAS
${formData.especificacoes_tecnicas || 'Conforme detalhado no Anexo I - Termo de Referência.'}

4. DO VALOR ESTIMADO
4.1. O valor total estimado para esta contratação é de R$ ${parseFloat(formData.valor_estimado || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}.

5. DOS PRAZOS
5.1. O prazo para entrega/execução é de ${formData.prazo_entrega || '30 (trinta) dias'}.
5.2. Local de entrega: ${formData.local_entrega || 'Conforme especificado no Termo de Referência'}.

6. DA PARTICIPAÇÃO
6.1. Poderão participar desta licitação empresas do ramo pertinente ao objeto licitado.
${formData.permite_consorcio ? '6.2. É permitida a participação de consórcios.' : '6.2. Não é permitida a participação de consórcios.'}
${formData.exige_visita_tecnica ? '6.3. É obrigatória a visita técnica ao local de execução dos serviços.' : ''}

7. DO JULGAMENTO
7.1. O julgamento será pelo critério de ${formData.criterio_julgamento.replace('_', ' ')}.

8. DAS DISPOSIÇÕES FINAIS
8.1. Este edital foi gerado automaticamente pelo Sistema de Licitações dos Correios.
8.2. Dúvidas e esclarecimentos: licitacao@correios.com.br

${formData.observacoes ? `\nOBSERVAÇÕES ADICIONAIS:\n${formData.observacoes}` : ''}

Brasília, ${new Date().toLocaleDateString('pt-BR')}

[Assinatura Digital]
Pregoeiro Responsável
        `.trim()
      };

      setEditalGerado(editalMock);
    } catch (err) {
      setError('Erro ao gerar edital: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!editalGerado) return;

    const element = document.createElement('a');
    const file = new Blob([editalGerado.conteudo], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = `Edital_${editalGerado.id}.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const handleNovoEdital = () => {
    setEditalGerado(null);
    setFormData({
      objeto: '',
      categoria: 'servicos',
      modalidade: 'pregao',
      valor_estimado: '',
      prazo_entrega: '',
      local_entrega: '',
      criterio_julgamento: 'menor_preco',
      exige_visita_tecnica: false,
      permite_consorcio: false,
      especificacoes_tecnicas: '',
      observacoes: ''
    });
  };

  if (editalGerado) {
    return (
      <div className="gerar-edital-container">
        <div className="edital-header">
          <h1>✅ Edital Gerado com Sucesso!</h1>
          <p>Seu edital foi processado pelos agentes de IA e está pronto para uso.</p>
        </div>

        <div className="edital-info">
          <div className="info-card">
            <h3>📋 Informações do Edital</h3>
            <div className="info-grid">
              <div className="info-item">
                <strong>ID:</strong> {editalGerado.id}
              </div>
              <div className="info-item">
                <strong>Objeto:</strong> {editalGerado.objeto}
              </div>
              <div className="info-item">
                <strong>Categoria:</strong> {editalGerado.categoria}
              </div>
              <div className="info-item">
                <strong>Modalidade:</strong> {editalGerado.modalidade}
              </div>
              <div className="info-item">
                <strong>Valor Estimado:</strong> R$ {parseFloat(editalGerado.valor_estimado || 0).toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
              </div>
              <div className="info-item">
                <strong>Data de Geração:</strong> {editalGerado.data_geracao}
              </div>
            </div>
          </div>

          <div className="edital-preview">
            <h3>📄 Preview do Edital</h3>
            <div className="preview-content">
              <pre>{editalGerado.conteudo}</pre>
            </div>
          </div>
        </div>

        <div className="edital-actions">
          <button className="action-button primary" onClick={handleDownload}>
            📥 Baixar Edital
          </button>
          <button className="action-button secondary" onClick={handleNovoEdital}>
            📝 Gerar Novo Edital
          </button>
          <button className="action-button secondary">
            📧 Enviar para Revisão
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="gerar-edital-container">
      <div className="edital-header">
        <h1>📝 Gerador Automatizado de Editais</h1>
        <p>Crie editais de licitação com inteligência artificial em minutos</p>
      </div>

      <form onSubmit={handleSubmit} className="edital-form">
        <div className="form-section">
          <h3>🎯 Informações Básicas</h3>
          
          <div className="form-group">
            <label htmlFor="objeto">Objeto da Licitação *</label>
            <input
              type="text"
              id="objeto"
              name="objeto"
              value={formData.objeto}
              onChange={handleInputChange}
              placeholder="Ex: Contratação de serviços de limpeza predial"
              required
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="categoria">Categoria</label>
              <select
                id="categoria"
                name="categoria"
                value={formData.categoria}
                onChange={handleInputChange}
              >
                <option value="servicos">Serviços</option>
                <option value="obras">Obras</option>
                <option value="bens">Bens</option>
                <option value="ti">Tecnologia da Informação</option>
                <option value="consultoria">Consultoria</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="modalidade">Modalidade</label>
              <select
                id="modalidade"
                name="modalidade"
                value={formData.modalidade}
                onChange={handleInputChange}
              >
                <option value="pregao">Pregão Eletrônico</option>
                <option value="concorrencia">Concorrência</option>
                <option value="tomada_precos">Tomada de Preços</option>
                <option value="convite">Convite</option>
                <option value="rdc">RDC</option>
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="valor_estimado">Valor Estimado (R$)</label>
              <input
                type="number"
                id="valor_estimado"
                name="valor_estimado"
                value={formData.valor_estimado}
                onChange={handleInputChange}
                placeholder="100000.00"
                step="0.01"
                min="0"
              />
            </div>

            <div className="form-group">
              <label htmlFor="criterio_julgamento">Critério de Julgamento</label>
              <select
                id="criterio_julgamento"
                name="criterio_julgamento"
                value={formData.criterio_julgamento}
                onChange={handleInputChange}
              >
                <option value="menor_preco">Menor Preço</option>
                <option value="melhor_tecnica">Melhor Técnica</option>
                <option value="tecnica_preco">Técnica e Preço</option>
                <option value="maior_desconto">Maior Desconto</option>
              </select>
            </div>
          </div>
        </div>

        <div className="form-section">
          <h3>📅 Prazos e Local</h3>
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="prazo_entrega">Prazo de Entrega/Execução</label>
              <input
                type="text"
                id="prazo_entrega"
                name="prazo_entrega"
                value={formData.prazo_entrega}
                onChange={handleInputChange}
                placeholder="Ex: 30 dias corridos"
              />
            </div>

            <div className="form-group">
              <label htmlFor="local_entrega">Local de Entrega/Execução</label>
              <input
                type="text"
                id="local_entrega"
                name="local_entrega"
                value={formData.local_entrega}
                onChange={handleInputChange}
                placeholder="Ex: Sede dos Correios - Brasília/DF"
              />
            </div>
          </div>
        </div>

        <div className="form-section">
          <h3>⚙️ Configurações Especiais</h3>
          
          <div className="form-row">
            <div className="form-group checkbox-group">
              <label>
                <input
                  type="checkbox"
                  name="exige_visita_tecnica"
                  checked={formData.exige_visita_tecnica}
                  onChange={handleInputChange}
                />
                Exige visita técnica
              </label>
            </div>

            <div className="form-group checkbox-group">
              <label>
                <input
                  type="checkbox"
                  name="permite_consorcio"
                  checked={formData.permite_consorcio}
                  onChange={handleInputChange}
                />
                Permite participação de consórcios
              </label>
            </div>
          </div>
        </div>

        <div className="form-section">
          <h3>📋 Especificações Técnicas</h3>
          
          <div className="form-group">
            <label htmlFor="especificacoes_tecnicas">Especificações Detalhadas</label>
            <textarea
              id="especificacoes_tecnicas"
              name="especificacoes_tecnicas"
              value={formData.especificacoes_tecnicas}
              onChange={handleInputChange}
              placeholder="Descreva as especificações técnicas detalhadas do objeto..."
              rows="6"
            />
          </div>

          <div className="form-group">
            <label htmlFor="observacoes">Observações Adicionais</label>
            <textarea
              id="observacoes"
              name="observacoes"
              value={formData.observacoes}
              onChange={handleInputChange}
              placeholder="Informações adicionais relevantes para o edital..."
              rows="4"
            />
          </div>
        </div>

        <div className="form-actions">
          <button type="submit" disabled={loading} className="submit-button">
            {loading ? (
              <>
                <span className="loading-spinner"></span>
                Gerando Edital...
              </>
            ) : (
              <>
                🤖 Gerar Edital com IA
              </>
            )}
          </button>
        </div>
      </form>

      {error && (
        <div className="error-message">
          ❌ {error}
        </div>
      )}

      {loading && (
        <div className="ai-processing">
          <h3>🤖 Agentes de IA Trabalhando...</h3>
          <div className="ai-steps">
            <div className="ai-step active">
              <span className="step-icon">👨‍💼</span>
              <span>Coletor de Requisitos analisando...</span>
            </div>
            <div className="ai-step active">
              <span className="step-icon">⚖️</span>
              <span>Analisador Jurídico verificando conformidade...</span>
            </div>
            <div className="ai-step active">
              <span className="step-icon">🔧</span>
              <span>Analisador Técnico validando especificações...</span>
            </div>
            <div className="ai-step">
              <span className="step-icon">📝</span>
              <span>Gerador de Edital criando documento...</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GerarEdital;
