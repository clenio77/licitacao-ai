import React, { useState } from 'react';
import './EditalWizard.css';

function EditalWizard({ formData, onNext, onBack, loading }) {
  const [wizardData, setWizardData] = useState({
    requisitos_tecnicos: formData?.requisitos_tecnicos || [],
    requisitos_juridicos: formData?.requisitos_juridicos || [],
    permite_consorcio: formData?.permite_consorcio || false,
    exige_visita_tecnica: formData?.exige_visita_tecnica || false,
    criterio_julgamento: formData?.criterio_julgamento || 'menor_preco',
    referencias_editais: formData?.referencias_editais || []
  });

  const handleInputChange = (field, value) => {
    setWizardData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const addRequisitoTecnico = () => {
    const novoRequisito = {
      descricao: '',
      obrigatorio: true,
      criterio_avaliacao: '',
      peso: 5
    };
    setWizardData(prev => ({
      ...prev,
      requisitos_tecnicos: [...prev.requisitos_tecnicos, novoRequisito]
    }));
  };

  const updateRequisitoTecnico = (index, field, value) => {
    const novosRequisitos = [...wizardData.requisitos_tecnicos];
    novosRequisitos[index] = {
      ...novosRequisitos[index],
      [field]: value
    };
    setWizardData(prev => ({
      ...prev,
      requisitos_tecnicos: novosRequisitos
    }));
  };

  const removeRequisitoTecnico = (index) => {
    setWizardData(prev => ({
      ...prev,
      requisitos_tecnicos: prev.requisitos_tecnicos.filter((_, i) => i !== index)
    }));
  };

  const addRequisitoJuridico = () => {
    const novoRequisito = {
      descricao: '',
      base_legal: '',
      obrigatorio: true,
      documentacao_necessaria: []
    };
    setWizardData(prev => ({
      ...prev,
      requisitos_juridicos: [...prev.requisitos_juridicos, novoRequisito]
    }));
  };

  const updateRequisitoJuridico = (index, field, value) => {
    const novosRequisitos = [...wizardData.requisitos_juridicos];
    novosRequisitos[index] = {
      ...novosRequisitos[index],
      [field]: value
    };
    setWizardData(prev => ({
      ...prev,
      requisitos_juridicos: novosRequisitos
    }));
  };

  const removeRequisitoJuridico = (index) => {
    setWizardData(prev => ({
      ...prev,
      requisitos_juridicos: prev.requisitos_juridicos.filter((_, i) => i !== index)
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onNext(wizardData);
  };

  return (
    <div className="edital-wizard">
      <form onSubmit={handleSubmit}>
        {/* Requisitos Técnicos */}
        <div className="wizard-section">
          <div className="section-header">
            <h3>🔧 Requisitos Técnicos</h3>
            <button type="button" onClick={addRequisitoTecnico} className="btn btn-secondary btn-sm">
              + Adicionar Requisito
            </button>
          </div>
          
          {wizardData.requisitos_tecnicos.length === 0 ? (
            <div className="empty-state">
              <p>Nenhum requisito técnico específico adicionado.</p>
              <p className="help-text">Clique em "Adicionar Requisito" para incluir especificações técnicas detalhadas.</p>
            </div>
          ) : (
            wizardData.requisitos_tecnicos.map((requisito, index) => (
              <div key={index} className="requisito-card">
                <div className="requisito-header">
                  <h4>Requisito Técnico {index + 1}</h4>
                  <button 
                    type="button" 
                    onClick={() => removeRequisitoTecnico(index)}
                    className="btn btn-danger btn-sm"
                  >
                    Remover
                  </button>
                </div>

                <div className="form-group">
                  <label>Descrição do Requisito *</label>
                  <textarea
                    value={requisito.descricao}
                    onChange={(e) => updateRequisitoTecnico(index, 'descricao', e.target.value)}
                    placeholder="Descreva o requisito técnico..."
                    rows={3}
                    required
                  />
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Tipo</label>
                    <select
                      value={requisito.obrigatorio ? 'obrigatorio' : 'desejavel'}
                      onChange={(e) => updateRequisitoTecnico(index, 'obrigatorio', e.target.value === 'obrigatorio')}
                    >
                      <option value="obrigatorio">Obrigatório</option>
                      <option value="desejavel">Desejável</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label>Peso na Avaliação (1-10)</label>
                    <input
                      type="number"
                      value={requisito.peso}
                      onChange={(e) => updateRequisitoTecnico(index, 'peso', parseInt(e.target.value))}
                      min="1"
                      max="10"
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label>Critério de Avaliação</label>
                  <input
                    type="text"
                    value={requisito.criterio_avaliacao}
                    onChange={(e) => updateRequisitoTecnico(index, 'criterio_avaliacao', e.target.value)}
                    placeholder="Como este requisito será avaliado..."
                  />
                </div>
              </div>
            ))
          )}
        </div>

        {/* Requisitos Jurídicos */}
        <div className="wizard-section">
          <div className="section-header">
            <h3>⚖️ Requisitos Jurídicos</h3>
            <button type="button" onClick={addRequisitoJuridico} className="btn btn-secondary btn-sm">
              + Adicionar Requisito
            </button>
          </div>
          
          {wizardData.requisitos_juridicos.length === 0 ? (
            <div className="empty-state">
              <p>Nenhum requisito jurídico específico adicionado.</p>
              <p className="help-text">Requisitos básicos de habilitação serão incluídos automaticamente.</p>
            </div>
          ) : (
            wizardData.requisitos_juridicos.map((requisito, index) => (
              <div key={index} className="requisito-card">
                <div className="requisito-header">
                  <h4>Requisito Jurídico {index + 1}</h4>
                  <button 
                    type="button" 
                    onClick={() => removeRequisitoJuridico(index)}
                    className="btn btn-danger btn-sm"
                  >
                    Remover
                  </button>
                </div>

                <div className="form-group">
                  <label>Descrição do Requisito *</label>
                  <textarea
                    value={requisito.descricao}
                    onChange={(e) => updateRequisitoJuridico(index, 'descricao', e.target.value)}
                    placeholder="Descreva o requisito jurídico..."
                    rows={3}
                    required
                  />
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label>Base Legal</label>
                    <input
                      type="text"
                      value={requisito.base_legal}
                      onChange={(e) => updateRequisitoJuridico(index, 'base_legal', e.target.value)}
                      placeholder="Lei, decreto, portaria..."
                    />
                  </div>

                  <div className="form-group">
                    <label>Tipo</label>
                    <select
                      value={requisito.obrigatorio ? 'obrigatorio' : 'desejavel'}
                      onChange={(e) => updateRequisitoJuridico(index, 'obrigatorio', e.target.value === 'obrigatorio')}
                    >
                      <option value="obrigatorio">Obrigatório</option>
                      <option value="desejavel">Desejável</option>
                    </select>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Configurações Gerais */}
        <div className="wizard-section">
          <h3>⚙️ Configurações Gerais</h3>
          
          <div className="form-row">
            <div className="form-group">
              <label>Critério de Julgamento</label>
              <select
                value={wizardData.criterio_julgamento}
                onChange={(e) => handleInputChange('criterio_julgamento', e.target.value)}
              >
                <option value="menor_preco">Menor Preço</option>
                <option value="melhor_tecnica">Melhor Técnica</option>
                <option value="tecnica_preco">Técnica e Preço</option>
                <option value="maior_lance">Maior Lance</option>
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group checkbox-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={wizardData.permite_consorcio}
                  onChange={(e) => handleInputChange('permite_consorcio', e.target.checked)}
                />
                <span className="checkmark"></span>
                Permite participação de consórcios
              </label>
              <p className="help-text">Marque se empresas podem se consorciar para participar</p>
            </div>

            <div className="form-group checkbox-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={wizardData.exige_visita_tecnica}
                  onChange={(e) => handleInputChange('exige_visita_tecnica', e.target.checked)}
                />
                <span className="checkmark"></span>
                Exige visita técnica obrigatória
              </label>
              <p className="help-text">Marque se é obrigatória a visita ao local</p>
            </div>
          </div>
        </div>

        {/* Referências */}
        <div className="wizard-section">
          <h3>📚 Editais de Referência</h3>
          
          <div className="form-group">
            <label>IDs de Editais Similares (opcional)</label>
            <textarea
              value={wizardData.referencias_editais.join('\n')}
              onChange={(e) => handleInputChange('referencias_editais', e.target.value.split('\n').filter(id => id.trim()))}
              placeholder="Digite os IDs de editais similares, um por linha..."
              rows={3}
            />
            <p className="help-text">O sistema usará estes editais como referência para melhorar a geração</p>
          </div>
        </div>

        {/* Botões de Ação */}
        <div className="wizard-actions">
          <button 
            type="button" 
            onClick={onBack}
            className="btn btn-secondary"
            disabled={loading}
          >
            ← Voltar
          </button>
          
          <button 
            type="submit" 
            className="btn btn-primary"
            disabled={loading}
          >
            {loading ? 'Gerando Edital...' : 'Gerar Edital →'}
          </button>
        </div>
      </form>
    </div>
  );
}

export default EditalWizard;
