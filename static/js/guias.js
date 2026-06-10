// Interactividad de las Guías APE: checkboxes con progreso (persisten en
// localStorage) + autoevaluación con feedback inmediato. Vanilla JS, sin deps.
(function () {
  'use strict';

  // ── Checklists / pasos con progreso persistente ──────────────
  function initChecklist(seccion) {
    var grupo = seccion.dataset.checkGroup;
    var slug = seccion.dataset.guia;
    var items = seccion.querySelectorAll('.check-item');
    var barra = seccion.querySelector('.progreso-barra');
    var texto = seccion.querySelector('.progreso-texto');

    function clave(i) { return 'guia:' + slug + ':' + grupo + ':' + i; }

    function actualizarProgreso() {
      var hechos = 0;
      items.forEach(function (it) { if (it.checked) hechos++; });
      var total = items.length;
      var pct = total ? Math.round((hechos / total) * 100) : 0;
      if (barra) barra.style.width = pct + '%';
      if (texto) texto.textContent = hechos + '/' + total + ' completado';
      seccion.classList.toggle('completo', total > 0 && hechos === total);
    }

    items.forEach(function (it) {
      var i = it.dataset.index;
      var li = it.closest('li');
      try { if (localStorage.getItem(clave(i)) === '1') it.checked = true; } catch (e) {}
      if (li) li.classList.toggle('hecho', it.checked);
      it.addEventListener('change', function () {
        try { localStorage.setItem(clave(i), it.checked ? '1' : '0'); } catch (e) {}
        if (li) li.classList.toggle('hecho', it.checked);
        actualizarProgreso();
      });
    });

    actualizarProgreso();
  }

  // ── Autoevaluación (feedback inmediato) ──────────────────────
  function initQuiz(pregunta) {
    var correcta = parseInt(pregunta.dataset.correcta, 10);
    var opciones = pregunta.querySelectorAll('.quiz-opcion');
    var explicacion = pregunta.querySelector('.quiz-explicacion');

    opciones.forEach(function (op) {
      op.addEventListener('click', function () {
        var elegida = parseInt(op.dataset.index, 10);
        opciones.forEach(function (o) { o.disabled = true; o.classList.remove('correcta', 'incorrecta'); });
        if (opciones[correcta]) opciones[correcta].classList.add('correcta');
        if (elegida !== correcta) op.classList.add('incorrecta');
        if (explicacion) explicacion.hidden = false;
        pregunta.classList.add('respondida');
      });
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.guia-interactivo[data-check-group]').forEach(initChecklist);
    document.querySelectorAll('.guia-quiz .quiz-pregunta').forEach(initQuiz);
  });
})();
