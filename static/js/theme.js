/* theme.js — toggle de modo claro/oscuro con persistencia en localStorage.
   El tema inicial ya lo aplica el script inline del <head> (anti-flash);
   aqui solo sincronizamos el boton y manejamos el click. */
(function () {
  'use strict';
  var STORAGE_KEY = 'theme';
  var SUN = '☀️';        // sol
  var MOON = '🌙';       // luna

  function currentTheme() {
    return document.documentElement.dataset.theme === 'dark' ? 'dark' : 'light';
  }

  function syncButton(theme) {
    var btn = document.getElementById('theme-toggle');
    if (!btn) return;
    var isDark = theme === 'dark';
    btn.setAttribute('aria-pressed', String(isDark));
    btn.setAttribute('aria-label', isDark ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro');
    var icon = btn.querySelector('.theme-icon');
    if (icon) icon.textContent = isDark ? SUN : MOON;
  }

  function applyTheme(theme) {
    document.documentElement.dataset.theme = theme;
    syncButton(theme);
  }

  function toggleTheme() {
    var next = currentTheme() === 'dark' ? 'light' : 'dark';
    try { localStorage.setItem(STORAGE_KEY, next); } catch (e) {}
    applyTheme(next);
  }

  document.addEventListener('DOMContentLoaded', function () {
    syncButton(currentTheme());
    var btn = document.getElementById('theme-toggle');
    if (btn) btn.addEventListener('click', toggleTheme);
  });

  /* Si el usuario NO fijo preferencia, seguir los cambios del sistema en vivo */
  if (window.matchMedia) {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function (e) {
      var saved;
      try { saved = localStorage.getItem(STORAGE_KEY); } catch (err) { saved = null; }
      if (saved !== 'dark' && saved !== 'light') applyTheme(e.matches ? 'dark' : 'light');
    });
  }
})();
