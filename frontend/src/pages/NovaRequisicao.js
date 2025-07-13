import React, { useState } from 'react';
import './NovaRequisicao.css';

const NovaRequisicao = () => {
  const [formData, setFormData] = useState({
    // Dados do solicitante
    solicitante_nome: '',
    solicitante_email: '',
    solicitante_cargo: '',
    setor_solicitante: '',
    telefone_contato: '',
    
    // Dados da requisição
    tipo_pedido: 'servico',
    objeto: '',
    justificativa: '',
    valor_estimado: '',
    prazo_necessidade: '',
    local_execucao: '',
    
    // Especificações técnicas
    especificacoes_tecnicas: '',
    quantidade: '',
    unidade_medida: '',
    criterios_selecao: [],
    
    // Observações
    observacoes: '',
    prioridade: 'normal',
    categoria: ''
  });

  const [loading, setLoading] = useState(false);
  const [requisicaoEnviada, setRequisicaoEnviada] = useState(null);
  const [error, setError] = useState(null);

  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleCriteriosChange = (e) => {
    const { value, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      criterios_selecao: checked 
        ? [...prev.criterios_selecao, value]
        : prev.criterios_selecao.filter(c => c !== value)
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Preparar dados para envio
      const requestData = {
        ...formData,
        valor_estimado: formData.valor_estimado ? parseFloat(formData.valor_estimado) : null,
        prazo_necessidade: formData.prazo_necessidade ? new Date(formData.prazo_necessidade).toISOString() : null
      };

      const response = await fetch(`${API_URL}/requisicoes/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setRequisicaoEnviada(data);
      
      // Limpar formulário
      setFormData({
        solicitante_nome: '',
        solicitante_email: '',
        solicitante_cargo: '',
        setor_solicitante: '',
        telefone_contato: '',
        tipo_pedido: 'servico',
        objeto: '',
        justificativa: '',
        valor_estimado: '',
        prazo_necessidade: '',
        local_execucao: '',
        especificacoes_tecnicas: '',
        quantidade: '',
        unidade_medida: '',
        criterios_selecao: [],
        observacoes: '',
        prioridade: 'normal',
        categoria: ''
      });

    } catch (err) {
      setError('Erro ao enviar requisição: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleNovaRequisicao = () => {
    setRequisicaoEnviada(null);
    setError(null);
  };

  if (requisicaoEnviada) {
    return (
      <div className="nova-requisicao-container">
        <div className="requisicao-enviada">
          <div className="success-header">
            <h1>✅ Requisição Enviada com Sucesso!</h1>
            <p>Sua requisição foi registrada e o processo de aprovação foi iniciado.</p>
          </div>

          <div className="requisicao-info">
            <div className="info-card">
              <h3>📋 Detalhes da Requisição</h3>
              <div className="info-grid">
                <div className="info-item">
                  <strong>Número da Requisição:</strong> {requisicaoEnviada.numero_requisicao}
                </div>
                <div className="info-item">
                  <strong>ID:</strong> {requisicaoEnviada.requisicao_id}
                </div>
                <div className="info-item">
                  <strong>Status:</strong> {requisicaoEnviada.status}
                </div>
                <div className="info-item">
                  <strong>Data de Criação:</strong> {new Date(requisicaoEnviada.data_criacao).toLocaleString('pt-BR')}
                </div>
              </div>
            </div>

            <div className="workflow-info">
              <h3>🔄 Próximos Passos</h3>
              <div className="workflow-steps">
                <div className="step active">
                  <span className="step-number">1</span>
                  <span className="step-text">Requisição Criada</span>
                </div>
                <div className="step">
                  <span className="step-number">2</span>
                  <span className="step-text">Aprovação do Supervisor</span>
                </div>
                <div className="step">
                  <span className="step-number">3</span>
                  <span className="step-text">Análise do Setor de Compras</span>
                </div>
                <div className="step">
                  <span className="step-number">4</span>
                  <span className="step-text">Validação Orçamentária</span>
                </div>
                <div className="step">
                  <span className="step-number">5</span>
                  <span className="step-text">Análise por Agentes IA</span>
                </div>
                <div className="step">
                  <span className="step-number">6</span>
                  <span className="step-text">Geração de Edital</span>
                </div>
              </div>
            </div>
          </div>

          <div className="requisicao-actions">
            <button className="action-button primary" onClick={handleNovaRequisicao}>
              📝 Nova Requisição
            </button>
            <button className="action-button secondary" onClick={() => window.open(`/requisicoes/${requisicaoEnviada.requisicao_id}`, '_blank')}>
              👁️ Acompanhar Status
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="nova-requisicao-container">
      <div className="requisicao-header">
        <h1>📝 Nova Requisição de Licitação</h1>
        <p>Preencha os dados abaixo para solicitar uma nova licitação</p>
      </div>

      <form onSubmit={handleSubmit} className="requisicao-form">
        {/* Seção 1: Dados do Solicitante */}
        <div className="form-section">
          <h3>👤 Dados do Solicitante</h3>
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="solicitante_nome">Nome Completo *</label>
              <input
                type="text"
                id="solicitante_nome"
                name="solicitante_nome"
                value={formData.solicitante_nome}
                onChange={handleInputChange}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="solicitante_email">E-mail *</label>
              <input
                type="email"
                id="solicitante_email"
                name="solicitante_email"
                value={formData.solicitante_email}
                onChange={handleInputChange}
                required
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="solicitante_cargo">Cargo</label>
              <input
                type="text"
                id="solicitante_cargo"
                name="solicitante_cargo"
                value={formData.solicitante_cargo}
                onChange={handleInputChange}
              />
            </div>

            <div className="form-group">
              <label htmlFor="setor_solicitante">Setor *</label>
              <select
                id="setor_solicitante"
                name="setor_solicitante"
                value={formData.setor_solicitante}
                onChange={handleInputChange}
                required
              >
                <option value="">Selecione o setor</option>
                <option value="TI">Tecnologia da Informação</option>
                <option value="RH">Recursos Humanos</option>
                <option value="Financeiro">Financeiro</option>
                <option value="Logística">Logística</option>
                <option value="Manutenção">Manutenção</option>
                <option value="Segurança">Segurança</option>
                <option value="Limpeza">Limpeza</option>
                <option value="Administrativo">Administrativo</option>
                <option value="Operações">Operações</option>
                <option value="Outro">Outro</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="telefone_contato">Telefone de Contato</label>
            <input
              type="tel"
              id="telefone_contato"
              name="telefone_contato"
              value={formData.telefone_contato}
              onChange={handleInputChange}
            />
          </div>
        </div>

        {/* Seção 2: Dados da Requisição */}
        <div className="form-section">
          <h3>📋 Dados da Requisição</h3>
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="tipo_pedido">Tipo de Pedido *</label>
              <select
                id="tipo_pedido"
                name="tipo_pedido"
                value={formData.tipo_pedido}
                onChange={handleInputChange}
                required
              >
                <option value="servico">Serviço</option>
                <option value="produto">Produto</option>
                <option value="obra">Obra</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="categoria">Categoria</label>
              <select
                id="categoria"
                name="categoria"
                value={formData.categoria}
                onChange={handleInputChange}
              >
                <option value="">Selecione a categoria</option>
                <option value="ti">Tecnologia da Informação</option>
                <option value="manutencao">Manutenção</option>
                <option value="limpeza">Limpeza</option>
                <option value="seguranca">Segurança</option>
                <option value="consultoria">Consultoria</option>
                <option value="equipamentos">Equipamentos</option>
                <option value="materiais">Materiais</option>
                <option value="obras">Obras</option>
              </select>
            </div>
          </div>

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

          <div className="form-group">
            <label htmlFor="justificativa">Justificativa da Necessidade *</label>
            <textarea
              id="justificativa"
              name="justificativa"
              value={formData.justificativa}
              onChange={handleInputChange}
              placeholder="Explique por que essa licitação é necessária..."
              rows="4"
              required
            />
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
              <label htmlFor="prazo_necessidade">Prazo de Necessidade</label>
              <input
                type="date"
                id="prazo_necessidade"
                name="prazo_necessidade"
                value={formData.prazo_necessidade}
                onChange={handleInputChange}
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="local_execucao">Local de Execução</label>
              <input
                type="text"
                id="local_execucao"
                name="local_execucao"
                value={formData.local_execucao}
                onChange={handleInputChange}
                placeholder="Ex: Sede dos Correios - Brasília/DF"
              />
            </div>

            <div className="form-group">
              <label htmlFor="prioridade">Prioridade</label>
              <select
                id="prioridade"
                name="prioridade"
                value={formData.prioridade}
                onChange={handleInputChange}
              >
                <option value="baixa">Baixa</option>
                <option value="normal">Normal</option>
                <option value="alta">Alta</option>
                <option value="urgente">Urgente</option>
              </select>
            </div>
          </div>
        </div>

        {/* Seção 3: Especificações Técnicas */}
        <div className="form-section">
          <h3>🔧 Especificações Técnicas</h3>
          
          <div className="form-group">
            <label htmlFor="especificacoes_tecnicas">Especificações Detalhadas</label>
            <textarea
              id="especificacoes_tecnicas"
              name="especificacoes_tecnicas"
              value={formData.especificacoes_tecnicas}
              onChange={handleInputChange}
              placeholder="Descreva as especificações técnicas detalhadas..."
              rows="6"
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="quantidade">Quantidade</label>
              <input
                type="text"
                id="quantidade"
                name="quantidade"
                value={formData.quantidade}
                onChange={handleInputChange}
                placeholder="Ex: 100"
              />
            </div>

            <div className="form-group">
              <label htmlFor="unidade_medida">Unidade de Medida</label>
              <select
                id="unidade_medida"
                name="unidade_medida"
                value={formData.unidade_medida}
                onChange={handleInputChange}
              >
                <option value="">Selecione</option>
                <option value="unidade">Unidade</option>
                <option value="metros">Metros</option>
                <option value="metros_quadrados">Metros Quadrados</option>
                <option value="litros">Litros</option>
                <option value="quilos">Quilos</option>
                <option value="pacotes">Pacotes</option>
                <option value="horas">Horas</option>
                <option value="dias">Dias</option>
                <option value="meses">Meses</option>
              </select>
            </div>
          </div>

          <div className="form-group">
            <label>Critérios de Seleção</label>
            <div className="checkbox-group">
              <label>
                <input
                  type="checkbox"
                  value="menor_preco"
                  checked={formData.criterios_selecao.includes('menor_preco')}
                  onChange={handleCriteriosChange}
                />
                Menor Preço
              </label>
              <label>
                <input
                  type="checkbox"
                  value="melhor_tecnica"
                  checked={formData.criterios_selecao.includes('melhor_tecnica')}
                  onChange={handleCriteriosChange}
                />
                Melhor Técnica
              </label>
              <label>
                <input
                  type="checkbox"
                  value="tecnica_preco"
                  checked={formData.criterios_selecao.includes('tecnica_preco')}
                  onChange={handleCriteriosChange}
                />
                Técnica e Preço
              </label>
              <label>
                <input
                  type="checkbox"
                  value="sustentabilidade"
                  checked={formData.criterios_selecao.includes('sustentabilidade')}
                  onChange={handleCriteriosChange}
                />
                Critérios Ambientais
              </label>
            </div>
          </div>
        </div>

        {/* Seção 4: Observações */}
        <div className="form-section">
          <h3>📝 Observações Adicionais</h3>
          
          <div className="form-group">
            <label htmlFor="observacoes">Informações Complementares</label>
            <textarea
              id="observacoes"
              name="observacoes"
              value={formData.observacoes}
              onChange={handleInputChange}
              placeholder="Informações adicionais relevantes para a licitação..."
              rows="4"
            />
          </div>
        </div>

        <div className="form-actions">
          <button type="submit" disabled={loading} className="submit-button">
            {loading ? (
              <>
                <span className="loading-spinner"></span>
                Enviando Requisição...
              </>
            ) : (
              <>
                📤 Enviar Requisição
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
    </div>
  );
};

export default NovaRequisicao;