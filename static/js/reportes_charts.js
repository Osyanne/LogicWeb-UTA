// Inicializa los gráficos Chart.js de la página "Mi Progreso".
// Lee los datos desde <script type="application/json" id="datos-progreso">.
(function () {
  var nodo = document.getElementById('datos-progreso');
  if (!nodo || typeof Chart === 'undefined') return;

  var datos = JSON.parse(nodo.textContent);
  var oscuro = document.documentElement.dataset.theme === 'dark';
  Chart.defaults.color = oscuro ? '#cbd5e1' : '#374151';
  Chart.defaults.font.family = "'Segoe UI', system-ui, sans-serif";

  var AZUL = '#4a90e2';

  // Barras: % de acierto por unidad
  var elBarras = document.getElementById('grafico-unidades');
  if (elBarras && datos.unidades.length) {
    new Chart(elBarras, {
      type: 'bar',
      data: {
        labels: datos.unidades,
        datasets: [{
          label: '% de acierto',
          data: datos.porcentajes,
          backgroundColor: AZUL,
          borderRadius: 6,
          maxBarThickness: 64,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, max: 100, ticks: { callback: function (v) { return v + '%'; } } },
        },
      },
    });
  }

  // Dona: aciertos vs. errores
  var elDona = document.getElementById('grafico-aciertos');
  if (elDona && (datos.correctos + datos.incorrectos) > 0) {
    new Chart(elDona, {
      type: 'doughnut',
      data: {
        labels: ['Aciertos', 'Errores'],
        datasets: [{
          data: [datos.correctos, datos.incorrectos],
          backgroundColor: ['#2e9e5b', '#d64545'],
          borderWidth: 2,
          borderColor: oscuro ? '#1e293b' : '#ffffff',
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '62%',
        plugins: { legend: { position: 'bottom' } },
      },
    });
  }
})();
