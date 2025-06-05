// Função para medir e reportar métricas de performance da aplicação React
// Para ativar, passe uma função de callback para reportWebVitals no index.js
// Exemplo: reportWebVitals(console.log)
const reportWebVitals = onPerfEntry => {
  if (onPerfEntry && onPerfEntry instanceof Function) {
    // Importa dinamicamente as funções do pacote web-vitals
    import('web-vitals').then(({ getCLS, getFID, getFCP, getLCP, getTTFB }) => {
      // Cada função mede um aspecto da performance:
      // CLS: Cumulative Layout Shift
      // FID: First Input Delay
      // FCP: First Contentful Paint
      // LCP: Largest Contentful Paint
      // TTFB: Time to First Byte
      getCLS(onPerfEntry);
      getFID(onPerfEntry);
      getFCP(onPerfEntry);
      getLCP(onPerfEntry);
      getTTFB(onPerfEntry);
    });
  }
};

export default reportWebVitals; 