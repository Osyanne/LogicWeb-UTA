# Modo Oscuro (OLED) — Plan de Implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Agregar un modo oscuro OLED a toda la app pública de LogicWeb UTA, que respete el sistema y se pueda alternar con un toggle persistente, sin tocar la base de datos.

**Architecture:** Se introduce una capa de variables CSS *semánticas* (`--bg`, `--surface`, `--text`, `--heading`, `--border`, etc.) en `:root` con los valores actuales (cero regresión en claro), y un bloque `html[data-theme="dark"]` que las redefine a la paleta OLED. Los componentes con color hardcodeado (chips, badges, avisos) reciben overrides explícitos en `[data-theme="dark"]`. Un script inline en el `<head>` aplica el tema antes de pintar (anti-flash); `theme.js` maneja el toggle y guarda la preferencia en `localStorage`.

**Tech Stack:** Django 6 templates, CSS3 (custom properties), JavaScript vanilla, `localStorage`, `matchMedia`.

**Verificación (no es TDD pytest):** este cambio es de presentación (CSS + JS de cliente) y el spec decidió **verificación visual** en vez de tests automatizados (el stack no tiene infra de test JS y `tests.py` sigue vacío). Cada tarea verifica con el navegador (preview tools / `runserver` + Playwright), alternando el tema y revisando contraste e "islas claras".

**Notas de entorno (gotchas conocidos):**
- Correr `python manage.py runserver` **desde `C:\Users\osyanne\proyecto_django`** (hay un `manage.py` huérfano en el home que secuestra el comando).
- El CSS se cachea agresivo en local → **hard reload (Ctrl+F5)** o `fetch(...,{cache:'no-store'})` tras cada cambio de CSS.
- Para ver el modo oscuro **antes** de tener el toggle (Tasks 1-6), activarlo a mano en la consola del navegador: `document.documentElement.dataset.theme = 'dark'` (y `'light'` para volver).
- Se trabaja en `main` local con commits frecuentes. **No pushear** hasta el visto bueno (un push a `main` dispara auto-deploy en Render).
- Estilo de commits del repo: Conventional Commits en español **sin acentos ni ñ**, **sin** `Co-Authored-By`.
- Todos los comandos `git` y `runserver` se ejecutan desde `proyecto_django`.

---

## File Structure

| Archivo | Responsabilidad | Acción |
|---|---|---|
| `static/css/style.css` | Capa semántica + bloque dark + overrides de componentes + CSS del toggle + migración de usos | Modify |
| `static/css/codigo.css` | Modo oscuro de pseudocódigo y aviso educativo (los bloques C++ ya son oscuros) | Modify |
| `static/css/contenidos.css` | Migración a semánticas + fix `var(--borde)` inexistente | Modify |
| `static/css/reportes.css` | Migración + barras/badges en oscuro + fix `var(--borde)` | Modify |
| `templates/base.html` | Script anti-flash en `<head>` + botón toggle en la navbar | Modify |
| `static/js/theme.js` | Lógica del toggle: resolver/aplicar/alternar tema + persistencia | **Create** |

---

## Task 1: Capa semántica + bloque oscuro + migración de `style.css`

**Files:**
- Modify: `static/css/style.css`

- [ ] **Step 1: Agregar las variables semánticas dentro de `:root`**

En `static/css/style.css`, dentro del bloque `:root { ... }` (justo antes de su `}` de cierre, después de la línea `--transicion: all 0.22s ease;`), agregar:

```css
  /* ── Capa semántica (theming claro/oscuro) ──────────────────── */
  --bg:           var(--gris-fondo);   /* fondo de página      */
  --surface:      var(--blanco);       /* tarjetas / paneles   */
  --surface-2:    var(--gris-fondo);   /* cajas internas       */
  --text:         var(--texto);        /* texto principal      */
  --text-muted:   var(--texto-suave);  /* texto secundario     */
  --heading:      var(--azul);         /* títulos              */
  --border:       var(--gris-borde);   /* bordes / divisores   */
  --shadow:       var(--sombra);
  --shadow-hover: var(--sombra-hover);
  --navbar-bg:    var(--azul);         /* fondo navbar/footer  */
  --accent:       var(--naranja);      /* naranja sólido       */
```

- [ ] **Step 2: Agregar el bloque de modo oscuro**

Inmediatamente **después** del cierre de `:root { ... }` (la línea `}`), agregar:

```css
/* ── Modo oscuro (OLED) — redefine solo las semánticas ──────── */
html[data-theme="dark"] {
  --bg:           #000000;
  --surface:      #121214;
  --surface-2:    #1b1b1f;
  --text:         #f0f0f2;
  --text-muted:   #9a9aa3;
  --heading:      #f4f4f6;
  --border:       #2a2a30;
  --shadow:       0 4px 20px rgba(0,0,0,.5);
  --shadow-hover: 0 8px 32px rgba(0,0,0,.6);
  --navbar-bg:    #0b1220;
  --accent:       #ff9a33;
}
```

- [ ] **Step 3: Migrar los usos NO ambiguos (reemplazo global en `style.css`)**

Reemplazar **todas** las ocurrencias en `style.css` (son seguras porque el texto a buscar incluye el paréntesis de cierre):

- `var(--texto)` → `var(--text)`
- `var(--texto-suave)` → `var(--text-muted)`
- `var(--gris-borde)` → `var(--border)`
- `var(--sombra)` → `var(--shadow)`
- `var(--sombra-hover)` → `var(--shadow-hover)`

> Nota: hacer primero `var(--texto-suave)` o usar coincidencia exacta con paréntesis, para no romper `--texto-suave` al reemplazar `--texto`. Buscar literalmente `var(--texto)` (con paréntesis) NO coincide con `var(--texto-suave)`.

- [ ] **Step 4: Migrar fondos de superficie (`var(--blanco)` como `background`)**

Solo donde `var(--blanco)` se usa como **`background`** (NO donde es `color:` — ese es texto blanco sobre acento y se mantiene). Cambiar `background: var(--blanco)` → `background: var(--surface)` en estos selectores:

`.card-acceso`, `.card-ejercicio`, `.ejercicio-header`, `.sidebar`, `.stat-card`, `.tabla-historial`, `.form-card`, y en `.form-group input, .form-group select, .input-respuesta`.

- [ ] **Step 5: Migrar fondos `var(--gris-fondo)` y títulos `var(--azul)`**

- `body { background: var(--gris-fondo) }` → `background: var(--bg)`
- `.ipo-box { background: var(--gris-fondo) }` → `background: var(--surface-2)`
- `.tabla-historial tr:hover td { background: var(--gris-fondo) }` → `background: var(--surface-2)`
- Títulos: cambiar `color: var(--azul)` → `color: var(--heading)` **solo** en: `.card-acceso h3`, `.card-ejercicio .titulo-ej`, `.ejercicio-header h1`, `.stat-card .numero`, `.form-card h2`, `.section-title`.
- `.section-title::after { background: var(--gris-borde) }` ya quedó como `var(--border)` por el Step 3.

- [ ] **Step 6: Migrar navbar y footer a `--navbar-bg`**

- `.navbar { background: var(--azul) }` → `background: var(--navbar-bg)`
- `footer { background: var(--azul) }` → `background: var(--navbar-bg)`

> Se mantienen en `var(--azul)` (acento de marca, se ve bien sobre negro): `.hero` (gradiente), `.unidades-strip`, `.sidebar-titulo`, `.tabla-historial th`, `.btn-primary`, `.badge-unidad:hover`. Y se mantiene `color: var(--blanco)` en todos lados (texto blanco sobre acento).

- [ ] **Step 7: Verificar — modo CLARO sin regresión**

Levantar el server desde `proyecto_django`:
```
python manage.py runserver
```
Abrir `http://127.0.0.1:8000/`, hacer **hard reload** (Ctrl+F5). Comparar con cómo se veía antes.
**Esperado:** la home en modo claro se ve **idéntica** a antes (mismos colores, sombras, títulos azules). Cero cambios visuales.

- [ ] **Step 8: Verificar — modo OSCURO base**

En la consola del navegador: `document.documentElement.dataset.theme = 'dark'`.
**Esperado:** fondo negro, navbar azul-negro, tarjetas gris muy oscuro (`#121214`), texto y títulos casi-blancos y legibles, naranja intacto. (Los chips todavía se ven mal — se arreglan en Task 2.) Volver con `= 'light'`.

- [ ] **Step 9: Commit**

```
git add static/css/style.css
git commit -m "feat(tema): capa de variables semanticas + base del modo oscuro"
```

---

## Task 2: Overrides de componentes con color fijo (`style.css`)

**Files:**
- Modify: `static/css/style.css`

- [ ] **Step 1: Agregar el bloque de overrides oscuros**

Al **final** de `static/css/style.css`, agregar:

```css
/* ── Overrides de componentes en modo oscuro ────────────────── */
/* Chips: fondo translucido del color + texto en version clara */
html[data-theme="dark"] .chip-resuelto    { background: rgba(59,130,246,.16); color: #7db3ff; }
html[data-theme="dark"] .chip-interactivo { background: rgba(168,85,247,.16); color: #c89bf5; }
html[data-theme="dark"] .chip-basico      { background: rgba(46,160,67,.16);  color: #6ee7a0; }
html[data-theme="dark"] .chip-medio       { background: rgba(245,158,11,.16); color: #fbbf24; }
html[data-theme="dark"] .chip-avanzado    { background: rgba(236,72,153,.16); color: #f49ac2; }
html[data-theme="dark"] .chip-unidad      { background: rgba(244,137,31,.16); color: #ffb066; }

/* Alerts */
html[data-theme="dark"] .alert-info    { background: rgba(59,130,246,.16); color: #7db3ff; }
html[data-theme="dark"] .alert-error   { background: rgba(239,68,68,.14);  color: #ff8a8a; }
html[data-theme="dark"] .alert-success { background: rgba(46,160,67,.16);  color: #6ee7a0; }

/* Retroalimentacion */
html[data-theme="dark"] .feedback-ok    { background: rgba(46,160,67,.10); }
html[data-theme="dark"] .feedback-err   { background: rgba(239,68,68,.10); }
html[data-theme="dark"] .feedback-ok h2 { color: #6ee7a0; }
html[data-theme="dark"] .feedback-err h2{ color: #ff8a8a; }

/* Sidebar de teoria: hover/activo (hoy usa naranja-suave, una isla clara) */
html[data-theme="dark"] .sidebar-item:hover,
html[data-theme="dark"] .sidebar-item.active { background: rgba(244,137,31,.16); color: var(--accent); }

/* Boton outline (azul sobre fondo oscuro = poco contraste) */
html[data-theme="dark"] .btn-outline { border-color: var(--text-muted); color: var(--text); }
html[data-theme="dark"] .btn-outline:hover { background: var(--accent); border-color: var(--accent); color: #1a1200; }

/* Inputs: foco mas visible en oscuro */
html[data-theme="dark"] .form-group input:focus,
html[data-theme="dark"] .input-respuesta:focus { box-shadow: 0 0 0 3px rgba(255,154,51,.25); border-color: var(--accent); }
```

- [ ] **Step 2: Verificar en oscuro**

`runserver` desde `proyecto_django`, abrir una lista de ejercicios (`/ejercicios/resueltos/`), activar `dataset.theme='dark'`, hard reload con `{cache:'no-store'}` si hace falta.
**Esperado:** los chips (Resuelto/Interactivo/Básico/Medio/Avanzado/Unidad) se ven como pastillas translúcidas con texto claro y buen contraste; ninguna "isla" pastel clara. Abrir una retroalimentación correcta e incorrecta (responder un interactivo) → cajas verde/roja oscuras legibles.

- [ ] **Step 3: Commit**

```
git add static/css/style.css
git commit -m "feat(tema): adaptar chips, alerts y retroalimentacion al modo oscuro"
```

---

## Task 3: Bloques de código (`codigo.css`)

**Files:**
- Modify: `static/css/codigo.css`

- [ ] **Step 1: Migrar superficies a semánticas**

En `static/css/codigo.css`:
- `.bloque-cpp { background: var(--blanco) }` → `background: var(--surface)`
- `.bloque-pseudo { background: var(--blanco) }` → `background: var(--surface)`
- `var(--sombra)` → `var(--shadow)` (en `.bloque-cpp` y `.bloque-pseudo`)

> Se mantienen tal cual los colores del editor de código C++ (`.bloque-cpp pre` `#1e1e1e`, header `#2d2d2d`, dots, y los `.hljs-*`): ya son oscuros y se ven bien en ambos temas.

- [ ] **Step 2: Agregar overrides oscuros para el pseudocódigo y el aviso**

Al final de `static/css/codigo.css`, agregar:

```css
/* ── Modo oscuro: pseudocodigo (hoy fondo claro) y aviso ────── */
html[data-theme="dark"] .bloque-pseudo pre      { background: var(--surface-2); }
html[data-theme="dark"] .bloque-pseudo pre code { color: var(--text); }
html[data-theme="dark"] .aviso-cpp { background: rgba(244,137,31,.12); color: #ffb066; }
```

- [ ] **Step 3: Verificar**

`runserver`, abrir un ejercicio resuelto con pseudocódigo y aviso (ej. `/ejercicios/resueltos/`, entrar a uno), activar oscuro.
**Esperado:** el bloque de código C++ se ve igual (oscuro), el contenedor exterior es gris oscuro; el **pseudocódigo** ya no es una caja blanca (fondo `#1b1b1f`, texto claro); el **aviso** "no se ejecuta" es naranja translúcido, no crema.

- [ ] **Step 4: Commit**

```
git add static/css/codigo.css
git commit -m "feat(tema): modo oscuro en pseudocodigo y aviso educativo"
```

---

## Task 4: Sección de Teoría (`contenidos.css`)

**Files:**
- Modify: `static/css/contenidos.css`

- [ ] **Step 1: Arreglar `var(--borde)` inexistente + migrar**

En `static/css/contenidos.css`, reemplazar **todas** las ocurrencias:
- `var(--borde)` → `var(--border)`  *(arregla el bug: `--borde` no existe → hoy esos bordes son transparentes)*
- `var(--texto)` → `var(--text)`
- `var(--texto-suave)` → `var(--text-muted)`
- `var(--sombra)` → `var(--shadow)`
- `background: var(--blanco)` → `background: var(--surface)` (en `.ruta-card`, `.tema-encabezado`, `.teoria-callout`, `.tema-nav a`)

Títulos (mantienen el azul de marca como acento de la sección, pero el azul oscuro es ilegible sobre tarjeta oscura) → cambiar `color: var(--azul)` a `color: var(--heading)` en: `.teoria-hero h1`, `.ruta-card h3`, `.tema-encabezado h1`. (Los `.unidad-tag`, `.callout-titulo`, `.cta` usan `var(--accent, var(--azul))` por unidad — se tratan en el Step 2.)

- [ ] **Step 2: Override oscuro para los acentos por unidad y la línea de la ruta**

Los acentos por unidad (`.u1`..`.u4`) son azul/naranja/verde/magenta y se usan como `color` de etiquetas pequeñas sobre tarjeta oscura. El azul (`.u1 #3a5998`) queda algo bajo de contraste. Aclarar los acentos solo en oscuro. Al final de `static/css/contenidos.css`, agregar:

```css
/* ── Modo oscuro: acentos por unidad mas claros + linea de ruta ── */
html[data-theme="dark"] .u1 { --accent: #7da0d4; }
html[data-theme="dark"] .u2 { --accent: #ffb066; }
html[data-theme="dark"] .u3 { --accent: #6ee7a0; }
html[data-theme="dark"] .u4 { --accent: #f49ac2; }
html[data-theme="dark"] .ruta-step .num { border-color: var(--surface); }
```

- [ ] **Step 3: Verificar**

`runserver`, abrir `/teoria/` (lista = ruta de aprendizaje) y entrar a una unidad (detalle), activar oscuro.
**Esperado:** la **línea vertical** de la ruta ahora se ve (antes transparente por el bug); las tarjetas de unidad son oscuras con borde-izquierdo de color por unidad; los números de paso, títulos, callout y nav prev/next legibles; sin islas claras.

- [ ] **Step 4: Commit**

```
git add static/css/contenidos.css
git commit -m "feat(tema): modo oscuro en teoria + fix var --borde inexistente"
```

---

## Task 5: Reportes / Mi Progreso (`reportes.css`)

**Files:**
- Modify: `static/css/reportes.css`

- [ ] **Step 1: Arreglar `var(--borde)` + migrar superficies**

En `static/css/reportes.css`, reemplazar **todas** las ocurrencias:
- `var(--borde)` → `var(--border)`
- `var(--texto)` → `var(--text)`  *(en `.unidad-label`)*
- `var(--texto-suave)` → `var(--text-muted)`  *(en `.stat-card .etiqueta`)*
- `var(--sombra)` → `var(--shadow)`
- `background: var(--blanco)` → `background: var(--surface)` (en `.stat-card`, `.progreso-unidades`, `.tabla-historial`)

> Se mantienen como acento de marca: `.stat-card .numero { color: var(--azul) }`, `.unidad-pct`, `.progreso-unidades h2` (azul) — sobre tarjeta oscura el azul puro es legible-justo; se aclaran en el Step 2. El `thead { background: var(--azul); color:#fff }` se mantiene.

- [ ] **Step 2: Overrides oscuros (barras, hover de tabla, badges, números)**

Al final de `static/css/reportes.css`, agregar:

```css
/* ── Modo oscuro: barras, tabla y badges ────────────────────── */
html[data-theme="dark"] .progress-bar-wrap,
html[data-theme="dark"] .unidad-bar-wrap { background: var(--surface-2); }
html[data-theme="dark"] .tabla-historial tbody tr:hover { background: rgba(255,255,255,.05); }
html[data-theme="dark"] .stat-card .numero,
html[data-theme="dark"] .unidad-pct,
html[data-theme="dark"] .progreso-unidades h2 { color: #7da0d4; }
html[data-theme="dark"] .badge-correcto   { background: rgba(46,160,67,.16); color: #6ee7a0; }
html[data-theme="dark"] .badge-incorrecto { background: rgba(239,68,68,.16); color: #ff8a8a; }
```

- [ ] **Step 3: Verificar**

Requiere usuario logueado. `runserver`, ingresar (usuario real existente, ej. `Osyan`) y abrir `/mi-progreso/`, activar oscuro.
**Esperado:** stat-cards oscuras con números azul-claro legibles; barras de progreso con canal oscuro y relleno degradado visible; tabla de historial oscura, hover sutil, badges correcto/incorrecto translúcidos. Sin fondos `#e0e0e0` ni `#f5f7ff` claros.

- [ ] **Step 4: Commit**

```
git add static/css/reportes.css
git commit -m "feat(tema): modo oscuro en reportes y mi progreso"
```

---

## Task 6: Script anti-flash en el `<head>` (`base.html`)

**Files:**
- Modify: `templates/base.html`

- [ ] **Step 1: Insertar el script inline lo antes posible en el `<head>`**

En `templates/base.html`, justo **después** de la línea `<meta name="viewport" ...>` (línea 6) y **antes** del primer `<link rel="stylesheet" ...>`, insertar:

```html
  <!-- Anti-flash: aplica el tema antes de pintar (lee localStorage o el sistema) -->
  <script>
    (function () {
      try {
        var t = localStorage.getItem('theme');
        if (t !== 'dark' && t !== 'light') {
          t = (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) ? 'dark' : 'light';
        }
        document.documentElement.dataset.theme = t;
      } catch (e) {}
    })();
  </script>
```

- [ ] **Step 2: Verificar que el tema se aplica al cargar**

Con un sistema en modo oscuro (o forzando: en consola `localStorage.setItem('theme','dark')` y recargar), abrir cualquier página.
**Esperado:** la página carga **directo en oscuro**, sin parpadeo blanco inicial. Inspeccionar `<html>`: tiene `data-theme="dark"`. Con `localStorage.setItem('theme','light')` + reload → carga en claro. Limpiar con `localStorage.removeItem('theme')`.

- [ ] **Step 3: Commit**

```
git add templates/base.html
git commit -m "feat(tema): script anti-flash de tema en el head"
```

---

## Task 7: Toggle en la navbar (`theme.js` + `base.html` + CSS)

**Files:**
- Create: `static/js/theme.js`
- Modify: `templates/base.html`
- Modify: `static/css/style.css`

- [ ] **Step 1: Crear `static/js/theme.js`**

```js
/* theme.js — toggle de modo claro/oscuro con persistencia en localStorage.
   El tema inicial ya lo aplica el script inline del <head> (anti-flash);
   aqui solo sincronizamos el boton y manejamos el click. */
(function () {
  'use strict';
  var STORAGE_KEY = 'theme';

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
    if (icon) icon.textContent = isDark ? '☀️' : '🌙'; /* sol / luna */
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
```

- [ ] **Step 2: Agregar el botón toggle en la navbar**

En `templates/base.html`, dentro de `<div class="navbar-user">` (línea 34), insertar el botón como **primer** hijo (antes del `{% if user.is_authenticated %}`):

```html
      <button id="theme-toggle" class="theme-toggle" type="button" aria-label="Cambiar a modo oscuro" aria-pressed="false">
        <span class="theme-icon" aria-hidden="true">&#127769;</span>
      </button>
```

- [ ] **Step 3: Cargar `theme.js`**

En `templates/base.html`, junto al `<script src="{% static 'js/main.js' %}"></script>` (línea 73), agregar **encima**:

```html
  <script src="{% static 'js/theme.js' %}"></script>
```

- [ ] **Step 4: Estilar el botón toggle**

Al final de `static/css/style.css`, agregar:

```css
/* ── Boton de cambio de tema (en la navbar) ─────────────────── */
.theme-toggle {
  background: rgba(255,255,255,.12);
  border: 1px solid rgba(255,255,255,.22);
  color: #fff;
  width: 36px; height: 36px;
  border-radius: 50%;
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
  display: inline-flex; align-items: center; justify-content: center;
  transition: var(--transicion);
}
.theme-toggle:hover { background: rgba(244,137,31,.28); border-color: var(--naranja); transform: translateY(-1px); }
```

- [ ] **Step 5: Verificar el toggle de punta a punta**

`runserver`, abrir la home. Limpiar estado: en consola `localStorage.removeItem('theme')` + reload.
**Esperado:**
- Aparece el botón 🌙/☀️ en la navbar (arriba a la derecha).
- Click → la página entera cambia a oscuro al instante; el ícono pasa a ☀️.
- Recargar (Ctrl+F5) → **sigue en oscuro** (persistió en `localStorage`).
- Click de nuevo → vuelve a claro; recargar → sigue claro.
- Navegar entre páginas (Teoría, Resueltos, Mi Progreso) → el tema se mantiene en todas.

- [ ] **Step 6: Commit**

```
git add static/js/theme.js templates/base.html static/css/style.css
git commit -m "feat(tema): toggle de modo oscuro en la navbar"
```

---

## Task 8: Barrido de verificación final + pulido

**Files:**
- (Posibles ajustes menores en cualquiera de los CSS según hallazgos)

- [ ] **Step 1: Recorrer toda la app en oscuro**

`runserver`. Con tema oscuro activo, recorrer y revisar cada página (logueado para ver progreso):
`/` (home) · `/teoria/` (ruta) · detalle de unidad · `/ejercicios/resueltos/` · detalle resuelto · `/ejercicios/interactivos/` · detalle interactivo · responder (retro ok **y** err) · `/mi-progreso/` · `/login/` · `/registro/`.

Checklist por página: ¿texto legible? ¿algún fondo/caja **claro** fuera de lugar? ¿chips/badges con contraste? ¿bordes visibles? ¿botones legibles?

- [ ] **Step 2: Verificar contraste y ausencia de flash**

- Texto principal `#f0f0f2` sobre `#000`/`#121214`: contraste muy alto (AA OK).
- Con `localStorage.theme='dark'`, recargar 3-4 páginas distintas: **cero** parpadeo blanco.
- Login y registro (formularios): inputs oscuros, labels y placeholders legibles, foco naranja visible.

- [ ] **Step 3: Aplicar pulidos detectados (si los hay)**

Si en el barrido aparece alguna isla clara o bajo contraste no cubierto, agregar el override puntual `html[data-theme="dark"] <selector> { ... }` en el CSS del archivo correspondiente. Si no hubo hallazgos, anotar "barrido limpio, sin cambios" y saltar al commit.

- [ ] **Step 4: Verificar modo claro intacto**

Recorrer 2-3 páginas en claro (`localStorage.removeItem('theme')` con sistema en claro, o `theme='light'`).
**Esperado:** todo idéntico al estado previo al modo oscuro (cero regresión).

- [ ] **Step 5: Commit final (si hubo pulidos)**

```
git add -A
git commit -m "fix(tema): ajustes finales de contraste en modo oscuro"
```

---

## Definición de "Hecho"

- Toggle 🌙/☀️ funcional en la navbar, persistente en `localStorage`, presente en todas las páginas.
- Primera visita respeta `prefers-color-scheme`; sin flash blanco al cargar en oscuro.
- Las 11 páginas públicas se ven bien en oscuro (sin islas claras, buen contraste) y **idénticas a antes** en claro.
- Cero cambios en modelos/BD/migraciones.
- Commits locales en `main` (sin pushear hasta el OK del usuario). Bug `var(--borde)` corregido de paso.
