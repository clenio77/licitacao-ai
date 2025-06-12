import React, { useState } from 'react';
import './EditalForm.css';

function EditalForm({ onSubmit, initialData, loading }) {
  const [formData, setFormData] = useState({
    objeto: initialData?.objeto || '',
    tipo_licitacao: initialData?.tipo_licitacao || 'pregao',
    modalidade: initialData?.modalidade || 'eletronica',
    categoria: initialData?.categoria || 'servicos',
    valor_total_estimado: initialData?.valor_total_estimado || '',
    prazo_execucao: initialData?.prazo_execucao || '',
    prazo_proposta: initialData?.prazo_proposta || 8,
    setor_requisitante: {
      nome: initialData?.setor_requisitante?.nome || '',
      responsavel: initialData?.setor_requisitante?.responsavel || '',
      email: initialData?.setor_requisitante?.email || '',
      telefone: initialData?.setor_requisitante?.telefone || '',
      justificativa: initialData?.setor_requisitante?.justificativa || ''
    },
    itens: initialData?.itens || [
      {
        numero: 1,
        descricao: '',
        unidade: 'un',
        quantidade: 1,
        valor_estimado_unitario: '',
        categoria: 'servicos'
      }
    ],
    observacoes: initialData?.observacoes || ''
  });

  const [errors, setErrors] = useState({});

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Limpar erro do campo quando usuário começar a digitar
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: null
      }));
    }
  };

  const handleSetorChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      setor_requisitante: {
        ...prev.setor_requisitante,
        [field]: value
      }
    }));
  };

  const handleItemChange = (index, field, value) => {
    const newItens = [...formData.itens];
    newItens[index] = {
      ...newItens[index],
      [field]: value
    };
    setFormData(prev => ({
      ...prev,
      itens: newItens
    }));
  };

  const addItem = () => {
    const newItem = {
      numero: formData.itens.length + 1,
      descricao: '',
      unidade: 'un',
      quantidade: 1,
      valor_estimado_unitario: '',
      categoria: formData.categoria
    };
    setFormData(prev => ({
      ...prev,
      itens: [...prev.itens, newItem]
    }));
  };

  const removeItem = (index) => {
    if (formData.itens.length > 1) {
      const newItens = formData.itens.filter((_, i) => i !== index);
      // Renumerar itens
      newItens.forEach((item, i) => {
        item.numero = i + 1;
      });
      setFormData(prev => ({
        ...prev,
        itens: newItens
      }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    // Validações obrigatórias
    if (!formData.objeto.trim()) {
      newErrors.objeto = 'Objeto é obrigatório';
    }

    if (!formData.setor_requisitante.nome.trim()) {
      newErrors.setor_nome = 'Nome do setor é obrigatório';
    }

    if (!formData.setor_requisitante.responsavel.trim()) {
      newErrors.setor_responsavel = 'Responsável é obrigatório';
    }

    if (!formData.setor_requisitante.email.trim()) {
      newErrors.setor_email = 'Email é obrigatório';
    } else if (!/\S+@\S+\.\S+/.test(formData.setor_requisitante.email)) {
      newErrors.setor_email = 'Email inválido';
    }

    if (!formData.setor_requisitante.justificativa.trim()) {
      newErrors.setor_justificativa = 'Justificativa é obrigatória';
    }

    // Validar itens
    formData.itens.forEach((item, index) => {
      if (!item.descricao.trim()) {
        newErrors[`item_${index}_descricao`] = 'Descrição do item é obrigatória';
      }
      if (!item.quantidade || item.quantidade <= 0) {
        newErrors[`item_${index}_quantidade`] = 'Quantidade deve ser maior que zero';
      }
    });

    // Validar valores numéricos
    if (formData.valor_total_estimado && formData.valor_total_estimado <= 0) {
      newErrors.valor_total_estimado = 'Valor deve ser maior que zero';
    }

    if (formData.prazo_execucao && formData.prazo_execucao <= 0) {
      newErrors.prazo_execucao = 'Prazo deve ser maior que zero';
    }

    if (formData.prazo_proposta < 5) {
      newErrors.prazo_proposta = 'Prazo mínimo de 5 dias para propostas';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (validateForm()) {
      // Converter valores numéricos
      const processedData = {
        ...formData,
        valor_total_estimado: formData.valor_total_estimado ? parseFloat(formData.valor_total_estimado) : null,
        prazo_execucao: formData.prazo_execucao ? parseInt(formData.prazo_execucao) : null,
        prazo_proposta: parseInt(formData.prazo_proposta),
        itens: formData.itens.map(item => ({
          ...item,
          quantidade: parseFloat(item.quantidade),
          valor_estimado_unitario: item.valor_estimado_unitario ? parseFloat(item.valor_estimado_unitario) : null
        }))
      };
      
      onSubmit(processedData);
    }
  };

  return (
    <div className="edital-form">
      <form onSubmit={handleSubmit}>
        {/* Dados Básicos */}
        <div className="form-section">
          <h3>📋 Dados Básicos da Licitação</h3>
          
          <div className="form-group">
            <label htmlFor="objeto">Objeto da Licitação *</label>
            <textarea
              id="objeto"
              value={formData.objeto}
              onChange={(e) => handleInputChange('objeto', e.target.value)}
              placeholder="Ex: Contratação de serviços de limpeza predial..."
              rows={3}
              className={errors.objeto ? 'error' : ''}
            />
            {errors.objeto && <span className="error-text">{errors.objeto}</span>}
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="tipo_licitacao">Tipo de Licitação</label>
              <select
                id="tipo_licitacao"
                value={formData.tipo_licitacao}
                onChange={(e) => handleInputChange('tipo_licitacao', e.target.value)}
              >
                <option value="pregao">Pregão</option>
                <option value="concorrencia">Concorrência</option>
                <option value="concurso">Concurso</option>
                <option value="leilao">Leilão</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="modalidade">Modalidade</label>
              <select
                id="modalidade"
                value={formData.modalidade}
                onChange={(e) => handleInputChange('modalidade', e.target.value)}
              >
                <option value="eletronica">Eletrônica</option>
                <option value="presencial">Presencial</option>
                <option value="hibrida">Híbrida</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="categoria">Categoria</label>
              <select
                id="categoria"
                value={formData.categoria}
                onChange={(e) => handleInputChange('categoria', e.target.value)}
              >
                <option value="servicos">Serviços</option>
                <option value="bens">Bens</option>
                <option value="obras">Obras</option>
                <option value="servicos_engenharia">Serviços de Engenharia</option>
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="valor_total_estimado">Valor Total Estimado (R$)</label>
              <input
                type="number"
                id="valor_total_estimado"
                value={formData.valor_total_estimado}
                onChange={(e) => handleInputChange('valor_total_estimado', e.target.value)}
                placeholder="0.00"
                step="0.01"
                min="0"
                className={errors.valor_total_estimado ? 'error' : ''}
              />
              {errors.valor_total_estimado && <span className="error-text">{errors.valor_total_estimado}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="prazo_execucao">Prazo de Execução (dias)</label>
              <input
                type="number"
                id="prazo_execucao"
                value={formData.prazo_execucao}
                onChange={(e) => handleInputChange('prazo_execucao', e.target.value)}
                placeholder="30"
                min="1"
                className={errors.prazo_execucao ? 'error' : ''}
              />
              {errors.prazo_execucao && <span className="error-text">{errors.prazo_execucao}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="prazo_proposta">Prazo para Propostas (dias)</label>
              <input
                type="number"
                id="prazo_proposta"
                value={formData.prazo_proposta}
                onChange={(e) => handleInputChange('prazo_proposta', e.target.value)}
                min="5"
                className={errors.prazo_proposta ? 'error' : ''}
              />
              {errors.prazo_proposta && <span className="error-text">{errors.prazo_proposta}</span>}
            </div>
          </div>
        </div>

        {/* Setor Requisitante */}
        <div className="form-section">
          <h3>🏢 Setor Requisitante</h3>
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="setor_nome">Nome do Setor *</label>
              <input
                type="text"
                id="setor_nome"
                value={formData.setor_requisitante.nome}
                onChange={(e) => handleSetorChange('nome', e.target.value)}
                placeholder="Ex: Gerência de Facilities"
                className={errors.setor_nome ? 'error' : ''}
              />
              {errors.setor_nome && <span className="error-text">{errors.setor_nome}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="setor_responsavel">Responsável *</label>
              <input
                type="text"
                id="setor_responsavel"
                value={formData.setor_requisitante.responsavel}
                onChange={(e) => handleSetorChange('responsavel', e.target.value)}
                placeholder="Nome do responsável"
                className={errors.setor_responsavel ? 'error' : ''}
              />
              {errors.setor_responsavel && <span className="error-text">{errors.setor_responsavel}</span>}
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="setor_email">Email *</label>
              <input
                type="email"
                id="setor_email"
                value={formData.setor_requisitante.email}
                onChange={(e) => handleSetorChange('email', e.target.value)}
                placeholder="email@correios.com.br"
                className={errors.setor_email ? 'error' : ''}
              />
              {errors.setor_email && <span className="error-text">{errors.setor_email}</span>}
            </div>

            <div className="form-group">
              <label htmlFor="setor_telefone">Telefone</label>
              <input
                type="tel"
                id="setor_telefone"
                value={formData.setor_requisitante.telefone}
                onChange={(e) => handleSetorChange('telefone', e.target.value)}
                placeholder="(11) 99999-9999"
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="setor_justificativa">Justificativa da Necessidade *</label>
            <textarea
              id="setor_justificativa"
              value={formData.setor_requisitante.justificativa}
              onChange={(e) => handleSetorChange('justificativa', e.target.value)}
              placeholder="Descreva a necessidade que motivou esta licitação..."
              rows={3}
              className={errors.setor_justificativa ? 'error' : ''}
            />
            {errors.setor_justificativa && <span className="error-text">{errors.setor_justificativa}</span>}
          </div>
        </div>

        {/* Itens */}
        <div className="form-section">
          <div className="section-header">
            <h3>📦 Itens da Licitação</h3>
            <button type="button" onClick={addItem} className="btn btn-secondary btn-sm">
              + Adicionar Item
            </button>
          </div>

          {formData.itens.map((item, index) => (
            <div key={index} className="item-card">
              <div className="item-header">
                <h4>Item {item.numero}</h4>
                {formData.itens.length > 1 && (
                  <button 
                    type="button" 
                    onClick={() => removeItem(index)}
                    className="btn btn-danger btn-sm"
                  >
                    Remover
                  </button>
                )}
              </div>

              <div className="form-group">
                <label>Descrição do Item *</label>
                <textarea
                  value={item.descricao}
                  onChange={(e) => handleItemChange(index, 'descricao', e.target.value)}
                  placeholder="Descreva detalhadamente o item..."
                  rows={2}
                  className={errors[`item_${index}_descricao`] ? 'error' : ''}
                />
                {errors[`item_${index}_descricao`] && (
                  <span className="error-text">{errors[`item_${index}_descricao`]}</span>
                )}
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Unidade</label>
                  <select
                    value={item.unidade}
                    onChange={(e) => handleItemChange(index, 'unidade', e.target.value)}
                  >
                    <option value="un">Unidade</option>
                    <option value="kg">Quilograma</option>
                    <option value="m">Metro</option>
                    <option value="m²">Metro Quadrado</option>
                    <option value="m³">Metro Cúbico</option>
                    <option value="l">Litro</option>
                    <option value="h">Hora</option>
                    <option value="mês">Mês</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Quantidade *</label>
                  <input
                    type="number"
                    value={item.quantidade}
                    onChange={(e) => handleItemChange(index, 'quantidade', e.target.value)}
                    min="0.01"
                    step="0.01"
                    className={errors[`item_${index}_quantidade`] ? 'error' : ''}
                  />
                  {errors[`item_${index}_quantidade`] && (
                    <span className="error-text">{errors[`item_${index}_quantidade`]}</span>
                  )}
                </div>

                <div className="form-group">
                  <label>Valor Unitário Estimado (R$)</label>
                  <input
                    type="number"
                    value={item.valor_estimado_unitario}
                    onChange={(e) => handleItemChange(index, 'valor_estimado_unitario', e.target.value)}
                    placeholder="0.00"
                    step="0.01"
                    min="0"
                  />
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Observações */}
        <div className="form-section">
          <h3>📝 Observações Adicionais</h3>
          
          <div className="form-group">
            <label htmlFor="observacoes">Observações</label>
            <textarea
              id="observacoes"
              value={formData.observacoes}
              onChange={(e) => handleInputChange('observacoes', e.target.value)}
              placeholder="Informações adicionais relevantes para a licitação..."
              rows={3}
            />
          </div>
        </div>

        {/* Botões */}
        <div className="form-actions">
          <button 
            type="submit" 
            className="btn btn-primary"
            disabled={loading}
          >
            {loading ? 'Processando...' : 'Continuar →'}
          </button>
        </div>
      </form>
    </div>
  );
}

export default EditalForm;
