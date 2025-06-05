// Ponto de entrada principal da aplicação React
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import reportWebVitals from './reportWebVitals';

// Cria a raiz React e renderiza o componente App dentro do elemento #root
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  // StrictMode ajuda a identificar problemas e boas práticas em desenvolvimento
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Opcional: coleta métricas de performance da aplicação
reportWebVitals();