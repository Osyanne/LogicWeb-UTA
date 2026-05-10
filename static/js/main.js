// main.js — LogicWeb UTA
// Validaciones client-side y utilidades del frontend

document.addEventListener('DOMContentLoaded', () => {

  // ── Marcar enlace activo en navbar ──────────────────────────
  const links = document.querySelectorAll('.navbar-links a');
  links.forEach(link => {
    if (link.href === window.location.href) {
      link.classList.add('active');
    }
  });

  // ── Auto-ocultar alertas después de 5 segundos ──────────────
  const alertas = document.querySelectorAll('.alert');
  alertas.forEach(alerta => {
    setTimeout(() => {
      alerta.style.transition = 'opacity .5s';
      alerta.style.opacity = '0';
      setTimeout(() => alerta.remove(), 500);
    }, 5000);
  });

  // ── Validación: no permitir espacios al inicio en respuestas ─
  const inputRespuesta = document.querySelector('.input-respuesta');
  if (inputRespuesta) {
    inputRespuesta.addEventListener('input', () => {
      inputRespuesta.style.borderColor = 'var(--gris-borde)';
    });
  }

  // ── Animación de entrada a las cards ─────────────────────────
  const cards = document.querySelectorAll('.card-acceso, .card-ejercicio');
  cards.forEach((card, i) => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(16px)';
    card.style.transition = `opacity .35s ease ${i * 0.06}s, transform .35s ease ${i * 0.06}s`;
    requestAnimationFrame(() => {
      card.style.opacity = '1';
      card.style.transform = 'translateY(0)';
    });
  });

});
