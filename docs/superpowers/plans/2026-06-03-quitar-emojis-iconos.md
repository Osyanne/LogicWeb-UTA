# Quitar Emojis → Íconos SVG — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reemplazar los ~79 emojis decorativos de LogicWeb UTA por una política híbrida (íconos SVG de línea en marca/títulos/estado/toggle; texto limpio en botones; color en lenguajes y unidades) para un look profesional.

**Architecture:** Íconos como partials `templates/icons/<nombre>.svg` incluidos con `{% include %}`, con `stroke:currentColor` para adaptarse a claro/oscuro. CSS de soporte en `style.css`. Tests de regresión en pytest puro de filesystem (sin Django). Verificación visual con Playwright.

**Tech Stack:** Django 6 templates, CSS3 (variables semánticas), SVG inline, pytest (filesystem), Playwright MCP.

**Spec:** `docs/superpowers/specs/2026-06-03-quitar-emojis-iconos-design.md`

**Working dir:** worktree `feat/paralelo-chat`. Tests se corren desde la raíz del worktree:
`python -m pytest tests/ -v` y `python manage.py check`.

**Regla de commits:** mensajes en estilo del repo (`feat(...)`, `refactor(...)`, `test(...)`). **NUNCA** agregar `Co-Authored-By`.

---

## File Structure

- **Create:** `templates/icons/{code,bar-chart,layers,log-in,user-plus,route,terminal,book,book-open,check-circle,x-circle,alert-triangle,x}.svg` (13 partials, una responsabilidad: un ícono c/u).
- **Create:** `tests/test_icon_partials.py`, `tests/test_no_emojis.py` (filesystem, sin Django).
- **Modify:** `static/css/style.css` (clases `.ico*`, `.lang-dot`, `.unidad-badge`, `.paso-num`).
- **Modify:** `static/js/theme.js` (SUN/MOON → SVG).
- **Modify:** `apps/ejercicios/comparaciones.py` (labels de lenguaje sin emoji).
- **Modify:** 13 templates (ver tareas 2–10).

**Out of scope:** `apps/ejercicios/admin.py` (interno + lo edita el otro chat). Sin cambios de modelos/migraciones.

**In-scope file list** (para el guard final):
```
templates/base.html
templates/inicio/index.html
templates/usuarios/login.html
templates/usuarios/registro.html
templates/contenidos/lista.html
templates/contenidos/detalle.html
templates/comparaciones/comparar.html
templates/retroalimentacion/respuesta.html
templates/reportes/mi_progreso.html
templates/ejercicios/interactivo.html
templates/ejercicios/resuelto.html
templates/ejercicios/lista_resueltos.html
templates/ejercicios/lista_interactivos.html
static/js/theme.js
apps/ejercicios/comparaciones.py
```

---

## Task 1: Fundación — partials de íconos + CSS

**Files:**
- Create: `templates/icons/*.svg` (13 archivos), `tests/test_icon_partials.py`
- Modify: `static/css/style.css`

- [ ] **Step 1: Write the failing test** — `tests/test_icon_partials.py`

```python
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
ICONS = ["code","bar-chart","layers","log-in","user-plus","route","terminal",
         "book","book-open","check-circle","x-circle","alert-triangle","x"]

def test_all_icon_partials_exist_and_are_svg():
    icondir = ROOT / "templates" / "icons"
    for name in ICONS:
        f = icondir / f"{name}.svg"
        assert f.exists(), f"falta {f}"
        s = f.read_text(encoding="utf-8")
        assert "<svg" in s and "</svg>" in s, f"{name}.svg no es SVG válido"
        assert 'stroke="currentColor"' in s, f"{name}.svg debe usar currentColor"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_icon_partials.py -v`
Expected: FAIL (carpeta `templates/icons` no existe).

- [ ] **Step 3: Create the 13 icon partials**

Cada archivo `templates/icons/<nombre>.svg` con este envoltorio (cambia solo el contenido interno):
```html
<svg class="{{ cls|default:'ico' }}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">INNER</svg>
```
INNER por ícono:
- **code:** `<polyline points="8 7 3 12 8 17"/><polyline points="16 7 21 12 16 17"/><line x1="13.5" y1="5" x2="10.5" y2="19"/>`
- **bar-chart:** `<line x1="3" y1="20" x2="21" y2="20"/><line x1="6" y1="20" x2="6" y2="13"/><line x1="12" y1="20" x2="12" y2="8"/><line x1="18" y1="20" x2="18" y2="4"/>`
- **layers:** `<polygon points="12 3 21 8 12 13 3 8"/><polyline points="3 12 12 17 21 12"/><polyline points="3 16 12 21 21 16"/>`
- **log-in:** `<path d="M15 3h4a1 1 0 0 1 1 1v16a1 1 0 0 1-1 1h-4"/><polyline points="10 17 15 12 10 7"/><line x1="15" y1="12" x2="3" y2="12"/>`
- **user-plus:** `<circle cx="9" cy="8" r="3.2"/><path d="M3.5 20v-1a5.5 5.5 0 0 1 11 0v1"/><line x1="19" y1="8" x2="19" y2="14"/><line x1="16" y1="11" x2="22" y2="11"/>`
- **route:** `<circle cx="6" cy="19" r="2.3"/><circle cx="18" cy="5" r="2.3"/><path d="M8.3 19H14a4 4 0 0 0 0-8H9a4 4 0 0 1 0-8h6.5"/>`
- **terminal:** `<polyline points="5 8 9 12 5 16"/><line x1="12" y1="16" x2="18" y2="16"/>`
- **book:** `<path d="M4 5a2 2 0 0 1 2-2h13v17H6a2 2 0 0 1-2-2z"/><line x1="9" y1="3" x2="9" y2="20"/>`
- **book-open:** `<path d="M12 7v13"/><path d="M3 5h5a3 3 0 0 1 3 3v12a2.5 2.5 0 0 0-2.5-2.5H3z"/><path d="M21 5h-5a3 3 0 0 0-3 3v12a2.5 2.5 0 0 1 2.5-2.5H21z"/>`
- **check-circle:** `<circle cx="12" cy="12" r="9"/><polyline points="8 12.5 11 15.5 16 9"/>`
- **x-circle:** `<circle cx="12" cy="12" r="9"/><line x1="9" y1="9" x2="15" y2="15"/><line x1="15" y1="9" x2="9" y2="15"/>`
- **alert-triangle:** `<path d="M12 3l9.2 16a1 1 0 0 1-.9 1.5H3.7a1 1 0 0 1-.9-1.5z"/><line x1="12" y1="9" x2="12" y2="14"/><line x1="12" y1="17.2" x2="12.01" y2="17.2"/>`
- **x:** `<line x1="6" y1="6" x2="18" y2="18"/><line x1="18" y1="6" x2="6" y2="18"/>`

- [ ] **Step 4: Add CSS to `static/css/style.css`** (al final del archivo)

```css
/* ── Íconos SVG (reemplazan emojis) ─────────────────────────── */
.ico{width:1.15em;height:1.15em;flex:0 0 auto;vertical-align:-.15em;display:inline-block}
.ico-sm{width:1em;height:1em}
.ico-lg{width:1.5em;height:1.5em;vertical-align:-.25em}
.brand-ico{width:1.3em;height:1.3em;color:var(--naranja)}
.ico-ok{color:var(--verde-ok)} .ico-err{color:var(--rojo-err)} .ico-warn{color:var(--naranja)}
.lang-dot{display:inline-block;width:.62em;height:.62em;border-radius:50%;margin-right:.4em;vertical-align:.02em;flex:0 0 auto}
.unidad-badge{display:inline-flex;align-items:center;justify-content:center;min-width:1.9em;height:1.9em;padding:0 .35em;border-radius:8px;font-weight:800;font-size:.85em;color:#fff;background:var(--azul-claro)}
.unidad-badge.u1{background:#3a5998}.unidad-badge.u2{background:#f4891f}.unidad-badge.u3{background:#2e7d32}.unidad-badge.u4{background:#b5179e}
.paso-num{font-size:1.6rem;font-weight:800;color:var(--accent);line-height:1}
```

- [ ] **Step 5: Run tests + check**

Run: `python -m pytest tests/test_icon_partials.py -v` → Expected: PASS
Run: `python manage.py check` → Expected: "System check identified no issues"

- [ ] **Step 6: Commit**

```bash
git add templates/icons tests/test_icon_partials.py static/css/style.css
git commit -m "feat(estilo): set de iconos SVG + CSS de soporte"
```

---

## Task 2: Navbar + toggle de tema

**Files:** Modify `templates/base.html`, `static/js/theme.js`; append a `tests/test_no_emojis.py`.

- [ ] **Step 1: Write `tests/test_no_emojis.py`** (helper + primer test)

```python
import re
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
EMOJI_RE = re.compile('[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U00002B00-\U00002BFF]')

def emojis_in(rel):
    return EMOJI_RE.findall((ROOT / rel).read_text(encoding="utf-8"))

def test_no_emoji_base_and_theme():
    assert emojis_in("templates/base.html") == []
    assert emojis_in("static/js/theme.js") == []
```

- [ ] **Step 2: Run → FAIL** — `python -m pytest tests/test_no_emojis.py::test_no_emoji_base_and_theme -v`

- [ ] **Step 3: Edit `templates/base.html`**
  - Marca (línea ~35): `🎓 Logic<span>Web</span> UTA` → `{% include "icons/code.svg" with cls="ico brand-ico" %} Logic<span>Web</span> UTA`
  - Usuario (línea ~53): `👤 {{ user... }}` → `{{ user... }}` (quitar `👤 `).

- [ ] **Step 4: Edit `static/js/theme.js`**
  - `var SUN = '☀️';` → `var SUN = '<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="4"/><line x1="12" y1="2" x2="12" y2="5"/><line x1="12" y1="19" x2="12" y2="22"/><line x1="2" y1="12" x2="5" y2="12"/><line x1="19" y1="12" x2="22" y2="12"/><line x1="4.9" y1="4.9" x2="7" y2="7"/><line x1="17" y1="17" x2="19.1" y2="19.1"/><line x1="4.9" y1="19.1" x2="7" y2="17"/><line x1="17" y1="7" x2="19.1" y2="4.9"/></svg>';`
  - `var MOON = '🌙';` → `var MOON = '<svg class="ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 12.8A8 8 0 1 1 11.2 3 6 6 0 0 0 21 12.8z"/></svg>';`
  - **Importante:** asegurar que el botón se actualice con `.innerHTML` (no `.textContent`). Si usa `textContent`, cambiarlo a `innerHTML`.

- [ ] **Step 5: Run → PASS + check**

`python -m pytest tests/test_no_emojis.py::test_no_emoji_base_and_theme -v` → PASS
`python manage.py check` → OK

- [ ] **Step 6: Commit**

```bash
git add templates/base.html static/js/theme.js tests/test_no_emojis.py
git commit -m "refactor(estilo): navbar y toggle de tema sin emojis"
```

---

## Task 3: Home (`inicio/index.html`)

**Files:** Modify `templates/inicio/index.html`; append test.

- [ ] **Step 1: Append test** a `tests/test_no_emojis.py`:
```python
def test_no_emoji_inicio():
    assert emojis_in("templates/inicio/index.html") == []
```
- [ ] **Step 2: Run → FAIL**
- [ ] **Step 3: Edit `templates/inicio/index.html`** (mapa exacto):
  - Botones: `🚀 Crear mi cuenta` → `Crear mi cuenta`; `⚙️ Practicar ahora` → `Practicar ahora`.
  - Chips de lenguaje del hero (`lang-chip`): `⚡ C++` → `<span class="lang-dot" style="background:#00599c"></span>C++`; `🐍 Python` → `<span class="lang-dot" style="background:#3572A5"></span>Python`; `☕ Java` → `<span class="lang-dot" style="background:#b07219"></span>Java`.
  - Pasos (`paso-icono`): `📚` → `<span class="paso-num">1</span>`; `⚙️` → `<span class="paso-num">2</span>`; `📊` → `<span class="paso-num">3</span>`.
  - Chips `chip-lang`: `🐍 Python`/`☕ Java` → dot + nombre (mismos colores).
- [ ] **Step 4: Run → PASS + `manage.py check`**
- [ ] **Step 5: Commit** — `git commit -am "refactor(estilo): home sin emojis (pasos numerados, dots de lenguaje)"`

---

## Task 4: Auth (`login.html`, `registro.html`)

**Files:** Modify `templates/usuarios/login.html`, `templates/usuarios/registro.html`; append test.

- [ ] **Step 1: Append test:**
```python
def test_no_emoji_auth():
    assert emojis_in("templates/usuarios/login.html") == []
    assert emojis_in("templates/usuarios/registro.html") == []
```
- [ ] **Step 2: Run → FAIL**
- [ ] **Step 3: Edits:**
  - `login.html`: `🔑 Iniciar Sesión` → `{% include "icons/log-in.svg" %} Iniciar Sesión`.
  - `registro.html`: `📝 Crear mi cuenta` (h2) → `{% include "icons/user-plus.svg" %} Crear mi cuenta`; botón `🚀 Crear mi cuenta` → `Crear mi cuenta`.
- [ ] **Step 4: Run → PASS + check**
- [ ] **Step 5: Commit** — `git commit -am "refactor(estilo): login y registro con iconos"`

---

## Task 5: Mi Progreso (`reportes/mi_progreso.html`)

**Files:** Modify `templates/reportes/mi_progreso.html`; append test.

- [ ] **Step 1: Append test** `test_no_emoji_progreso` (scan `templates/reportes/mi_progreso.html`).
- [ ] **Step 2: Run → FAIL**
- [ ] **Step 3: Edits:**
  - `📊 Mi Progreso — LogicWeb UTA` → `{% include "icons/bar-chart.svg" %} Mi Progreso — LogicWeb UTA`.
  - `✅ Aciertos` → `{% include "icons/check-circle.svg" with cls="ico ico-sm ico-ok" %} Aciertos`.
  - `❌ Errores` → `{% include "icons/x-circle.svg" with cls="ico ico-sm ico-err" %} Errores`.
  - `📚 Progreso por Unidad` → `{% include "icons/layers.svg" %} Progreso por Unidad`.
  - `✅ Visto` → `Visto` (texto plano; o check-circle sm si se ve mejor).
  - badge `✅ Correcto` → `{% include "icons/check-circle.svg" with cls="ico ico-sm ico-ok" %} Correcto`.
  - badge `❌ Incorrecto` → `{% include "icons/x-circle.svg" with cls="ico ico-sm ico-err" %} Incorrecto`.
  - Botones: `📥 Descargar historial CSV` → `Descargar historial CSV`; `⚙️ Seguir practicando` → `Seguir practicando`.
- [ ] **Step 4: Run → PASS + check**
- [ ] **Step 5: Commit** — `git commit -am "refactor(estilo): mi progreso con iconos de estado"`

---

## Task 6: Teoría (`contenidos/lista.html`, `detalle.html`)

**Files:** Modify ambos; append test.

- [ ] **Step 1: Append test** `test_no_emoji_contenidos` (scan ambos archivos).
- [ ] **Step 2: Run → FAIL**
- [ ] **Step 3: Edits:**
  - `lista.html`: `🛤️ Ruta de Aprendizaje` → `{% include "icons/route.svg" %} Ruta de Aprendizaje`.
  - `lista.html` + `detalle.html`, badge de unidad: el bloque `{% if tema.unidad == 1 %}🧠{% elif tema.unidad == 2 %}⚙️{% elif tema.unidad == 3 %}🧩{% else %}📦{% endif %}` → `<span class="unidad-badge u{{ tema.unidad }}">U{{ tema.unidad }}</span>`.
  - `lista.html`: `📝 {{ tema.ejercicios.count }} ejercicio(s)` → `{{ tema.ejercicios.count }} ejercicio(s)`.
  - `detalle.html`: `📖 Teoría de la unidad` → `{% include "icons/book.svg" %} Teoría de la unidad`.
- [ ] **Step 4: Run → PASS + check**
- [ ] **Step 5: Commit** — `git commit -am "refactor(estilo): teoria con ruta/libro y badges de unidad"`

---

## Task 7: Comparar (`comparaciones/comparar.html` + `comparaciones.py`)

**Files:** Modify `templates/comparaciones/comparar.html`, `apps/ejercicios/comparaciones.py`; append test.

- [ ] **Step 1: Append test:**
```python
def test_no_emoji_comparar():
    assert emojis_in("templates/comparaciones/comparar.html") == []
    assert emojis_in("apps/ejercicios/comparaciones.py") == []
```
- [ ] **Step 2: Run → FAIL**
- [ ] **Step 3: Edits:**
  - `comparaciones.py`: en los 8 labels, `"⚡ C++"` → `"C++"` y `"☕ Java"` → `"Java"`.
  - `comparar.html`: sub-etiquetas → quitar emoji: `📝 Problema:` → `Problema:` (mantener `<b>`); `💭 ` (antes de `<b>Idea:</b>`) → quitar; `🔍 ¿Qué cambia y por qué?` → `¿Qué cambia y por qué?`.
  - `comparar.html`: donde se renderiza el label de cada lenguaje (`{{ ... .label }}`), anteponer `<span class="lang-dot" style="background:{{ <var_lenguaje>.color }}"></span>` (el dict ya trae `color`). Leer el template para el nombre exacto de la variable del loop.
- [ ] **Step 4: Run → PASS + check**
- [ ] **Step 5: Commit** — `git commit -am "refactor(estilo): comparar sin emojis, dots por color de lenguaje"`

---

## Task 8: Resueltos (`resuelto.html`, `lista_resueltos.html`)

**Files:** Modify ambos; append test.

- [ ] **Step 1: Append test** `test_no_emoji_resueltos` (scan ambos).
- [ ] **Step 2: Run → FAIL**
- [ ] **Step 3: Edits:**
  - `lista_resueltos.html`: `💡 Ejercicios Resueltos — Código paso a paso` → `{% include "icons/book-open.svg" %} Ejercicios Resueltos — Código paso a paso`.
  - `lista_resueltos.html`: filtros `🐍 Python`/`☕ Java` y chips `🐍 Python`/`☕ Java` → dot (`#3572A5`/`#b07219`) + nombre.
  - `lista_resueltos.html`: `✕ Unidad` → `{% include "icons/x.svg" with cls="ico ico-sm" %} Unidad`.
  - `lista_resueltos.html`: chip `📘 Resuelto` → `Resuelto`.
  - `resuelto.html`: chip `📘 Ejercicio Resuelto` → `Ejercicio Resuelto`.
  - `resuelto.html`: h4 `📥 Entrada` → `Entrada`; `⚙️ Proceso` → `Proceso`; `📤 Salida` → `Salida`; `📝 Pseudocódigo` → `Pseudocódigo`.
  - `resuelto.html`: aviso `⚠️ Este código es contenido educativo...` → `{% include "icons/alert-triangle.svg" with cls="ico ico-warn" %} Este código es contenido educativo...`.
  - `resuelto.html`: botón `⚙️ Ir a práctica interactiva` → `Ir a práctica interactiva`.
- [ ] **Step 4: Run → PASS + check**
- [ ] **Step 5: Commit** — `git commit -am "refactor(estilo): resueltos sin emojis (titulos, h4, aviso)"`

---

## Task 9: Interactivos (`interactivo.html`, `lista_interactivos.html`)

**Files:** Modify ambos; append test.

- [ ] **Step 1: Append test** `test_no_emoji_interactivos` (scan ambos).
- [ ] **Step 2: Run → FAIL**
- [ ] **Step 3: Edits:**
  - `lista_interactivos.html`: `⚙️ Práctica Interactiva — Analiza código y Responde` → `{% include "icons/terminal.svg" %} Práctica Interactiva — Analiza código y Responde`.
  - `lista_interactivos.html`: `💡 ` antes de "Regístrate..." → quitar; filtros/chips `🐍 Python`/`☕ Java` → dot + nombre; `✕ Unidad` → `{% include "icons/x.svg" with cls="ico ico-sm" %} Unidad`; chip `⚙️ Interactivo` → `Interactivo`.
  - `interactivo.html`: chip `⚙️ Ejercicio Interactivo` → `Ejercicio Interactivo`.
  - `interactivo.html`: h3 `★ Código Python/Java/C++ — Estúdialo antes de responder` → quitar `★ ` (queda el texto).
  - `interactivo.html`: `💡 Lee y traza el algoritmo...` → quitar `💡 `.
  - `interactivo.html`: botón `✅ Verificar respuesta` → `Verificar respuesta`.
  - `interactivo.html`: `¿Atascado? Pide una pista 👇` → quitar ` 👇`.
  - `interactivo.html`: botón `💡 Pedir una pista` → `Pedir una pista`.
  - `interactivo.html` (JS): `btnPista.textContent = '✓ No hay más pistas';` → `'No hay más pistas'`.
- [ ] **Step 4: Run → PASS + check**
- [ ] **Step 5: Commit** — `git commit -am "refactor(estilo): interactivos sin emojis"`

---

## Task 10: Respuesta (`retroalimentacion/respuesta.html`)

**Files:** Modify `templates/retroalimentacion/respuesta.html`; append test.

- [ ] **Step 1: Append test** `test_no_emoji_respuesta` (scan el archivo).
- [ ] **Step 2: Run → FAIL**
- [ ] **Step 3: Edits:**
  - `🎉 ¡Correcto!` → `{% include "icons/check-circle.svg" with cls="ico ico-lg ico-ok" %} ¡Correcto!`.
  - `✗ Incorrecto` → `{% include "icons/x-circle.svg" with cls="ico ico-lg ico-err" %} Incorrecto`.
  - `💡 <strong>Recomendación:</strong>` → quitar `💡 `.
  - Botones: `📋 Ver todos los ejercicios` → `Ver todos los ejercicios`; `📊 Ver mi progreso` → `Ver mi progreso`.
- [ ] **Step 4: Run → PASS + check**
- [ ] **Step 5: Commit** — `git commit -am "refactor(estilo): pantalla de respuesta con iconos de estado"`

---

## Task 11: Guard de regresión + verificación visual

**Files:** Modify `tests/test_no_emojis.py`.

- [ ] **Step 1: Append guard parametrizado** a `tests/test_no_emojis.py`:

```python
import pytest
IN_SCOPE = [
    "templates/base.html","templates/inicio/index.html",
    "templates/usuarios/login.html","templates/usuarios/registro.html",
    "templates/contenidos/lista.html","templates/contenidos/detalle.html",
    "templates/comparaciones/comparar.html","templates/retroalimentacion/respuesta.html",
    "templates/reportes/mi_progreso.html","templates/ejercicios/interactivo.html",
    "templates/ejercicios/resuelto.html","templates/ejercicios/lista_resueltos.html",
    "templates/ejercicios/lista_interactivos.html","static/js/theme.js",
    "apps/ejercicios/comparaciones.py",
]

@pytest.mark.parametrize("rel", IN_SCOPE)
def test_no_decorative_emoji_anywhere(rel):
    assert emojis_in(rel) == [], f"quedó un emoji en {rel}"
```

- [ ] **Step 2: Run toda la suite → PASS**

Run: `python -m pytest tests/ -v` → Expected: todos PASS
Run: `python manage.py check` → OK

- [ ] **Step 3: Verificación visual (Playwright)**

Levantar server propio (puerto libre, p.ej. 8780) y revisar en **claro y oscuro**:
```bash
python manage.py runserver 8780
```
Páginas a revisar: `/` (home), `/contenidos/` (ruta+unidades), un `/contenidos/<id>` (teoría), `/comparar/`, un interactivo, un resuelto, `/login/`, y `/mi-progreso/` (logueado). Para cada una: navegar con Playwright, togglear tema, screenshot. **Confirmar:** ningún emoji visible; íconos nítidos (sobre todo `code`, `route`, `terminal`, `book-open`, `alert-triangle`); dots de lenguaje con color; badges U1–U4 con su color; pasos 1·2·3; estado verde/rojo correcto; íconos legibles en oscuro. Si algún ícono se ve mal, ajustar su `templates/icons/<n>.svg` y re-screenshot.

- [ ] **Step 4: Commit** (si hubo ajustes de íconos)

```bash
git add tests/test_no_emojis.py templates/icons
git commit -m "test(estilo): guard de regresion anti-emoji + ajustes de iconos"
```

---

## Self-Review (completado al escribir el plan)

- **Cobertura del spec:** marca ✔(T2) · usuario ✔(T2) · títulos ✔(T4-T9) · botones ✔(T3-T10) · estado ✔(T5,T10) · lenguajes ✔(T3,T7,T8,T9) · pasos ✔(T3) · unidades ✔(T6) · sub-etiquetas ✔(T7,T8,T9) · toggle ✔(T2) · filtro ✕ ✔(T8,T9). Inventario de íconos ✔(T1). Test de regresión ✔(T11). Verificación claro/oscuro ✔(T11). `admin.py` excluido ✔.
- **Sin placeholders:** cada edit tiene string origen→destino; cada ícono su SVG; tests con código real.
- **Consistencia de nombres:** clases (`.ico`, `.ico-ok/err/warn`, `.lang-dot`, `.unidad-badge.uN`, `.paso-num`, `.brand-ico`) y nombres de íconos coinciden entre T1 y su uso en T2-T10. Helper `emojis_in` definido en T2, reusado en T3-T11.
