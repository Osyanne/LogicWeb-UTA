# Rediseño de la Home — Plan de Implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rediseñar la home como "portada que engancha" (hero + chips de lenguaje + cómo funciona + ejercicios destacados + stats), sin duplicar la navegación del navbar/Teoría.

**Architecture:** El view `inicio` pasa `destacados` (uno por lenguaje) + `num_unidades` + `total_ejercicios`. El template `index.html` se reescribe con 4 secciones y carga un CSS nuevo `home.css` que usa las **variables semánticas** del modo oscuro (funciona en claro y oscuro sin overrides). Se quitan la tira de unidades y el grid de accesos.

**Tech Stack:** Django 6 (template + view), CSS3 (custom properties semánticas), sin JS nuevo.

**Verificación (no es TDD pytest):** cambio de presentación (view simple + template + CSS). Verificación **visual** con preview/Playwright en claro y oscuro, logueado y no, + `manage.py check`. (El proyecto no tiene suite de tests; `tests.py` vacío.)

**Notas de entorno (gotchas del modo oscuro):**
- Correr `runserver` **desde `C:\Users\osyanne\proyecto_django`** (hay un `manage.py` huérfano en el home).
- `runserver --noreload` **cachea templates en memoria** → reiniciar el server (preview_stop+start) tras editar `index.html`.
- CSS se cachea agresivo → cache-bust `?v=` o Ctrl+F5 al verificar.
- Las preview tools se cuelgan en páginas con highlight.js, pero la home **no** tiene código → screenshot OK; aun así Playwright es el fallback confiable.
- Estilo de commits: Conventional Commits en español **sin acentos ni ñ**, **sin** `Co-Authored-By`.
- Se trabaja en una rama nueva; no pushear hasta el OK.

---

## File Structure

| Archivo | Responsabilidad | Acción |
|---|---|---|
| `apps/ejercicios/views.py` | View `inicio`: pasa destacados (1/lenguaje), num_unidades, total_ejercicios | Modify |
| `templates/inicio/index.html` | Home: hero+chips, cómo funciona, destacados, stats (quita unidades-strip y accesos-grid) | Modify (reescribir) |
| `static/css/home.css` | Estilos de las secciones nuevas, con variables semánticas | **Create** |

---

## Task 1: View `inicio` — destacados + num_unidades

**Files:**
- Modify: `apps/ejercicios/views.py` (función `inicio`, líneas 11-17)

- [ ] **Step 1: Reemplazar el cuerpo de `inicio()`**

En `apps/ejercicios/views.py`, reemplazar:

```python
def inicio(request):
    unidades = Tema.objects.values('unidad').distinct().order_by('unidad')
    total_ejercicios = Ejercicio.objects.filter(activo=True).count()
    return render(request, 'inicio/index.html', {
        'unidades': unidades,
        'total_ejercicios': total_ejercicios,
    })
```

por:

```python
def inicio(request):
    total_ejercicios = Ejercicio.objects.filter(activo=True).count()
    num_unidades = Tema.objects.values('unidad').distinct().count()
    # Ejercicios destacados: uno por lenguaje, prefiriendo resueltos (mejor vitrina)
    destacados = []
    for lang in ('cpp', 'python', 'java'):
        ej = (Ejercicio.objects.filter(activo=True, lenguaje=lang, categoria='resuelto')
              .select_related('tema').first()
              or Ejercicio.objects.filter(activo=True, lenguaje=lang)
              .select_related('tema').first())
        if ej:
            destacados.append(ej)
    return render(request, 'inicio/index.html', {
        'total_ejercicios': total_ejercicios,
        'num_unidades': num_unidades,
        'destacados': destacados,
    })
```

(`Ejercicio` y `Tema` ya están importados al inicio de `views.py`.)

- [ ] **Step 2: Verificar el contexto por shell**

Run (desde `proyecto_django`):
```
python manage.py shell -c "from apps.ejercicios.models import Ejercicio; print([(e.lenguaje, e.categoria, e.titulo) for lang in ('cpp','python','java') for e in [Ejercicio.objects.filter(activo=True, lenguaje=lang, categoria='resuelto').first() or Ejercicio.objects.filter(activo=True, lenguaje=lang).first()] if e])"
```
Expected: una lista de hasta 3 tuplas, una por lenguaje (cpp, python, java), cada una con su título. Confirma que hay un ejercicio por lenguaje.

- [ ] **Step 3: Commit**

```
git add apps/ejercicios/views.py
git commit -m "feat(home): el view inicio pasa destacados (1 por lenguaje) y num_unidades"
```

---

## Task 2: `home.css` (nuevo) + reescribir `index.html`

**Files:**
- Create: `static/css/home.css`
- Modify: `templates/inicio/index.html` (reescribir completo)

- [ ] **Step 1: Crear `static/css/home.css`**

```css
/* ═══════════════════════════════════════════════════════
   home.css — Portada de LogicWeb UTA
   Usa las variables semanticas (claro + oscuro).
   ═══════════════════════════════════════════════════════ */

/* Chips de lenguaje en el hero (sobre el gradiente azul, en ambos temas) */
.hero-langs { display: flex; gap: .5rem; justify-content: center; flex-wrap: wrap; margin-top: 1.5rem; }
.hero-langs .lang-chip {
  background: rgba(255,255,255,.14);
  color: #fff;
  padding: .35rem .9rem;
  border-radius: 20px;
  font-size: .85rem;
  font-weight: 700;
}

/* Bloque de seccion */
.home-section { padding: 2.25rem 0 .5rem; }
.home-section-title { text-align: center; font-size: 1.5rem; font-weight: 800; color: var(--heading); margin-bottom: 1.5rem; }

/* Encabezado de seccion con linea + enlace */
.section-head { display: flex; align-items: center; gap: .75rem; margin: 1rem 0 1.1rem; }
.section-head h2 { font-size: 1.35rem; font-weight: 800; color: var(--heading); }
.section-head .linea { flex: 1; height: 2px; background: var(--border); }
.section-head .ver-todos { color: var(--azul-claro); font-weight: 700; font-size: .9rem; white-space: nowrap; }

/* Como funciona (3 pasos) */
.pasos-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }
.paso-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radio);
  padding: 1.5rem 1.25rem;
  text-align: center;
  box-shadow: var(--shadow);
  transition: var(--transicion);
}
.paso-card:hover { transform: translateY(-3px); box-shadow: var(--shadow-hover); }
.paso-card .paso-icono { font-size: 2.2rem; line-height: 1; }
.paso-card h3 { font-size: 1rem; font-weight: 800; color: var(--heading); margin: .55rem 0 .3rem; }
.paso-card p { font-size: .88rem; color: var(--text-muted); }

/* Ejercicios destacados */
.destacados-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.25rem; }
.card-destacado {
  background: var(--surface);
  border: 1px solid var(--border);
  border-left: 4px solid var(--azul-claro);
  border-radius: var(--radio);
  padding: 1.25rem;
  box-shadow: var(--shadow);
  transition: var(--transicion);
  display: flex;
  flex-direction: column;
  gap: .5rem;
  text-decoration: none;
}
.card-destacado:hover { transform: translateY(-3px); box-shadow: var(--shadow-hover); }
.card-destacado.cpp    { border-left-color: #00599c; }
.card-destacado.python { border-left-color: #3572a5; }
.card-destacado.java   { border-left-color: #b07219; }
.card-destacado .chips { display: flex; gap: .4rem; flex-wrap: wrap; }
.card-destacado .titulo { font-weight: 800; color: var(--heading); font-size: 1rem; }
.card-destacado .desc { font-size: .85rem; color: var(--text-muted); line-height: 1.5; }

/* Chip de lenguaje (solido, color de marca; legible en ambos temas) */
.chip-lang { color: #fff; font-size: .72rem; font-weight: 700; padding: .15rem .55rem; border-radius: 10px; letter-spacing: .3px; }
.chip-lang.cpp    { background: #00599c; }
.chip-lang.python { background: #3572a5; }
.chip-lang.java   { background: #b07219; }

/* Banner de stats */
.stats-banner {
  background: linear-gradient(135deg, var(--azul), var(--azul-medio));
  border-radius: var(--radio);
  padding: 1.75rem;
  display: flex;
  justify-content: space-around;
  text-align: center;
  color: #fff;
  margin: 1rem 0;
  gap: 1rem;
  flex-wrap: wrap;
}
.stats-banner .num { font-size: 2rem; font-weight: 800; color: var(--naranja); line-height: 1; }
.stats-banner .lbl { font-size: .85rem; opacity: .88; margin-top: .25rem; }

/* Responsivo basico (el pulido movil completo es el sub-proyecto 3) */
@media (max-width: 720px) {
  .pasos-grid, .destacados-grid { grid-template-columns: 1fr; }
}
```

- [ ] **Step 2: Reescribir `templates/inicio/index.html`**

Reemplazar TODO el contenido del archivo por:

```html
{% extends 'base.html' %}
{% load static %}
{% block titulo %}Inicio{% endblock %}

{% block head_extra %}
<link rel="stylesheet" href="{% static 'css/home.css' %}">
{% endblock %}

{% block contenido %}

<!-- Hero -->
<section class="hero">
  <h1>Bienvenido a <span>LogicWeb UTA</span></h1>
  <p>Aprende logica de programacion analizando y practicando con ejercicios reales en C++, Python y Java</p>
  {% if not user.is_authenticated %}
    <div class="flex-gap" style="justify-content:center">
      <a href="{% url 'registro' %}" class="btn btn-naranja">🚀 Crear mi cuenta</a>
      <a href="{% url 'login' %}" class="btn btn-outline" style="border-color:#fff;color:#fff">Ingresar</a>
    </div>
  {% else %}
    <a href="{% url 'ejercicios_interactivos' %}" class="btn btn-naranja">⚙️ Practicar ahora</a>
  {% endif %}
  <div class="hero-langs">
    <span class="lang-chip">⚡ C++</span>
    <span class="lang-chip">🐍 Python</span>
    <span class="lang-chip">☕ Java</span>
  </div>
</section>

<div class="container">

  <!-- Como funciona -->
  <section class="home-section">
    <h2 class="home-section-title">¿Como funciona?</h2>
    <div class="pasos-grid">
      <div class="paso-card">
        <div class="paso-icono">📚</div>
        <h3>1 · Estudia la teoria</h3>
        <p>Logica, algoritmos, pseudocodigo y POO, organizados por unidad.</p>
      </div>
      <div class="paso-card">
        <div class="paso-icono">⚙️</div>
        <h3>2 · Practica</h3>
        <p>Analiza codigo real y responde ejercicios interactivos, con pistas.</p>
      </div>
      <div class="paso-card">
        <div class="paso-icono">📊</div>
        <h3>3 · Mide tu avance</h3>
        <p>Revisa tus aciertos, errores y tu progreso por unidad.</p>
      </div>
    </div>
  </section>

  <!-- Ejercicios destacados -->
  {% if destacados %}
  <section class="home-section">
    <div class="section-head">
      <h2>Date una idea</h2>
      <span class="linea"></span>
      <a href="{% url 'ejercicios_resueltos' %}" class="ver-todos">Ver todos →</a>
    </div>
    <div class="destacados-grid">
      {% for ej in destacados %}
        {% if ej.categoria == 'resuelto' %}
        <a href="{% url 'resuelto_detalle' ej.pk %}" class="card-destacado {{ ej.lenguaje }}">
        {% else %}
        <a href="{% url 'interactivo_detalle' ej.pk %}" class="card-destacado {{ ej.lenguaje }}">
        {% endif %}
          <div class="chips">
            {% if ej.lenguaje == 'python' %}<span class="chip-lang python">🐍 Python</span>
            {% elif ej.lenguaje == 'java' %}<span class="chip-lang java">☕ Java</span>
            {% else %}<span class="chip-lang cpp">C++</span>{% endif %}
            <span class="chip chip-{{ ej.dificultad }}">{{ ej.get_dificultad_display }}</span>
          </div>
          <div class="titulo">{{ ej.titulo }}</div>
          <div class="desc">{{ ej.enunciado|truncatechars:90 }}</div>
        </a>
      {% endfor %}
    </div>
  </section>
  {% endif %}

  <!-- Banner de stats -->
  <section class="home-section">
    <div class="stats-banner">
      <div><div class="num">{{ total_ejercicios }}</div><div class="lbl">Ejercicios</div></div>
      <div><div class="num">{{ num_unidades }}</div><div class="lbl">Unidades</div></div>
      <div><div class="num">3</div><div class="lbl">Lenguajes</div></div>
    </div>
  </section>

</div>

{% endblock %}
```

> Nota: los textos van **sin acentos** para evitar cualquier problema de encoding al escribir el archivo; si se prefieren con acentos, escribir el archivo en UTF-8 explícito. (El resto del proyecto usa acentos en templates, así que es seguro usarlos — pero por consistencia con los commits, el plan los omite.)

- [ ] **Step 3: Reiniciar el server (template cacheado)**

`preview_stop` del server actual y `preview_start name="logicweb"` (o reiniciar el `runserver`). Necesario porque `--noreload` no relee `index.html`.

- [ ] **Step 4: Verificar en claro (no autenticado)**

Abrir `http://localhost:8000/` (sin sesión). Hard reload.
**Esperado:** hero con título "Bienvenido a LogicWeb UTA" + botones "Crear mi cuenta"/"Ingresar" + 3 chips de lenguaje; sección "¿Cómo funciona?" con 3 cards; "Date una idea" con 3 cards (una por lenguaje, con su color de borde) + "Ver todos →"; banner de stats con números. **NO** debe aparecer la tira de badges U1-U4 ni el grid "¿Qué quieres hacer hoy?".

- [ ] **Step 5: Verificar en oscuro**

En consola: `document.documentElement.dataset.theme='dark'` (o con el toggle). Reusar el detector de islas claras:
```js
(() => { const bad=[]; for (const el of document.querySelectorAll('main *')) { const bg=getComputedStyle(el).backgroundColor; const m=bg.match(/rgba?\((\d+), (\d+), (\d+)(?:, ([\d.]+))?\)/); if(!m) continue; const r=+m[1],g=+m[2],b=+m[3],a=m[4]===undefined?1:+m[4]; if(a>0.5 && (r+g+b)/3>200) bad.push({cls:el.className,bg}); } return bad.length; })()
```
Expected: `0` (cero islas claras). Las paso-card y card-destacado deben ser oscuras (var(--surface)), texto legible.

- [ ] **Step 6: Verificar autenticado**

Con sesión iniciada, recargar `/`. **Esperado:** el hero muestra "⚙️ Practicar ahora" en vez de los dos botones. El resto igual.

- [ ] **Step 7: Commit**

```
git add static/css/home.css templates/inicio/index.html
git commit -m "feat(home): redisenar la home como portada (hero+chips, como funciona, destacados, stats)"
```

---

## Task 3: Verificación integral + pulido

**Files:** (posibles ajustes en `home.css`)

- [ ] **Step 1: System check + barrido**

Run (desde `proyecto_django`): `python manage.py check` → Expected: `System check identified no issues`.
Recorrer `/` en claro y oscuro, logueado y no. Confirmar: cero islas claras (detector del Task 2 Step 5), enlaces de destacados van al detalle correcto, "Ver todos →" va a `/ejercicios/resueltos/`.

- [ ] **Step 2: Responsive básico**

Con el navegador en ~390px de ancho (móvil), abrir `/`.
**Esperado:** las grids (`.pasos-grid`, `.destacados-grid`) colapsan a 1 columna; el banner de stats no desborda; nada se sale de pantalla. (El pulido móvil completo es el sub-proyecto 3 — acá solo que no se rompa.)

- [ ] **Step 3: Aplicar pulidos detectados (si los hay)**

Si aparece una isla clara o un desborde, agregar el ajuste puntual en `home.css` (override `html[data-theme="dark"] <sel>` o regla responsive). Si no hubo hallazgos, anotar "barrido limpio" y saltar.

- [ ] **Step 4: Commit final (si hubo pulidos)**

```
git add -A
git commit -m "fix(home): ajustes de contraste/responsive en la portada"
```

---

## Definición de "Hecho"

- Home rediseñada como portada (hero+chips, cómo funciona, destacados 1/lenguaje, stats); sin la tira de unidades ni el grid de accesos.
- Se ve bien en **claro y oscuro**, **logueado y no**, sin islas claras.
- Destacados enlazan al detalle correcto; "Ver todos →" a resueltos.
- No se rompe en ancho de móvil.
- `manage.py check` limpio; cero regresión en otras páginas.
- Commits en rama (sin pushear hasta el OK).
