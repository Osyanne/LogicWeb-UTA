(function () {
  const btn = document.getElementById('noti-toggle');
  const dropdown = document.getElementById('noti-dropdown');
  if (!btn || !dropdown) return;

  function abrir() { dropdown.hidden = false; btn.setAttribute('aria-expanded', 'true'); }
  function cerrar() { dropdown.hidden = true; btn.setAttribute('aria-expanded', 'false'); }

  btn.addEventListener('click', function (e) {
    e.stopPropagation();
    if (dropdown.hidden) { abrir(); } else { cerrar(); }
  });
  document.addEventListener('click', function (e) {
    if (!dropdown.hidden && !dropdown.contains(e.target)) { cerrar(); }
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { cerrar(); }
  });
})();
