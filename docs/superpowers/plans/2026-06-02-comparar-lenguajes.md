# Comparar Lenguajes — Plan de Implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Página `/comparar/` "Un problema, tres lenguajes": el mismo algoritmo resuelto en C++/Python/Java lado a lado, con código comentado, explicación por lenguaje y análisis de diferencias.

**Architecture:** Contenido **curado** en un módulo Python (`comparaciones.py`, constante `PROBLEMAS`). Un view simple lo pasa al template, que arma tabs + una sección por problema con 3 columnas. Resaltado con highlight.js (se agregan python+java). CSS nuevo con variables semánticas (claro+oscuro). Acceso desde los chips del hero.

**Tech Stack:** Django 6 (view + template + datos Python), CSS3 (custom properties), JS vanilla (tab-switcher), highlight.js (CDN).

**Verificación (no es TDD pytest):** la lógica del view es trivial (pasa una constante); el grueso es contenido + presentación. Verificación: **shell** (la estructura de datos) + **visual** (Playwright/preview en claro y oscuro). No hay suite pytest.

**Notas de entorno (gotchas conocidos):**
- `runserver` **desde `C:\Users\osyanne\proyecto_django`** (manage.py huérfano en el home).
- `--noreload` cachea templates → reiniciar el server tras editar el template.
- CSS cacheado → cache-bust `?v=` / Ctrl+F5.
- Server frío: el 1er navigate de Playwright puede dar timeout → `browser_close` + reintentar.
- Commits sin acentos/ñ, sin `Co-Authored-By`. Rama nueva; no pushear hasta el OK.

---

## File Structure

| Archivo | Responsabilidad | Acción |
|---|---|---|
| `apps/ejercicios/comparaciones.py` | Constante `PROBLEMAS` (contenido curado de los 4 problemas) | **Create** |
| `apps/ejercicios/views.py` | View `comparar` (pasa PROBLEMAS) | Modify |
| `apps/ejercicios/urls.py` | Ruta `/comparar/` | Modify |
| `templates/comparaciones/comparar.html` | Página: hero + tabs + secciones (3 columnas) + JS | **Create** |
| `static/css/comparar.css` | Estilos (tabs, grid 3 col, responsive, claro/oscuro) | **Create** |
| `templates/inicio/index.html` | Chips de lenguaje del hero → enlaces a `/comparar/` | Modify |

---

## Task 1: Datos + view + URL

**Files:**
- Create: `apps/ejercicios/comparaciones.py`
- Modify: `apps/ejercicios/views.py`, `apps/ejercicios/urls.py`

- [ ] **Step 1: Crear `apps/ejercicios/comparaciones.py`**

Cada problema es un dict con `slug, titulo, nivel, enunciado, idea, lenguajes (lista de {id,label,color,codigo,como}), diferencias (lista de {titulo,detalle})`. El **primer problema va completo** (plantilla); curar los otros 3 con la MISMA estructura (specs en el Step siguiente).

```python
# apps/ejercicios/comparaciones.py
# Contenido curado para la pagina "Un problema, tres lenguajes".
# NO se ejecuta: es texto educativo que el estudiante lee.

PROBLEMAS = [
    {
        "slug": "par-impar",
        "titulo": "Es par o impar",
        "nivel": "Basico",
        "enunciado": "Leer un numero entero y mostrar si es par o impar.",
        "idea": "Un numero es par si el resto de dividirlo entre 2 es cero. El operador modulo (%) devuelve ese resto, y existe en los tres lenguajes.",
        "lenguajes": [
            {
                "id": "cpp", "label": "⚡ C++", "color": "#00599c",
                "codigo": (
                    "#include <iostream>      // entrada/salida\n"
                    "using namespace std;\n"
                    "int main() {\n"
                    "    int n;               // el tipo es obligatorio\n"
                    "    cin >> n;            // lee del teclado\n"
                    "    // ternario: condicion ? si : no\n"
                    "    cout << (n % 2 == 0 ? \"Par\" : \"Impar\");\n"
                    "    return 0;\n"
                    "}"
                ),
                "como": "Declara el tipo (int), incluye <iostream> para cin/cout y resuelve con un operador ternario. Compila a binario nativo.",
            },
            {
                "id": "python", "label": "\U0001f40d Python", "color": "#3572a5",
                "codigo": (
                    "# input() lee texto; int() lo convierte\n"
                    "n = int(input())\n"
                    "# expresion condicional en una linea\n"
                    "print(\"Par\" if n % 2 == 0 else \"Impar\")"
                ),
                "como": "No declara tipos: int(input()) lee y convierte. Lo resuelve en 2 lineas con una expresion condicional. Es interpretado.",
            },
            {
                "id": "java", "label": "☕ Java", "color": "#b07219",
                "codigo": (
                    "import java.util.Scanner;\n"
                    "public class Main {\n"
                    "    public static void main(String[] args) {\n"
                    "        Scanner sc = new Scanner(System.in);\n"
                    "        int n = sc.nextInt();   // tipado estatico\n"
                    "        System.out.println(n % 2 == 0 ? \"Par\" : \"Impar\");\n"
                    "    }\n"
                    "}"
                ),
                "como": "Todo vive dentro de una class y del metodo main. Usa Scanner para leer. Tipado estatico; corre sobre la JVM.",
            },
        ],
        "diferencias": [
            {"titulo": "Entrada/salida", "detalle": "C++ cin/cout, Python input()/print(), Java Scanner/System.out."},
            {"titulo": "Tipos", "detalle": "C++ y Java obligan a declararlos (int); Python los infiere solo."},
            {"titulo": "Estructura", "detalle": "Python va directo; C++ necesita main(); Java ademas exige una class."},
            {"titulo": "Concision", "detalle": "Python (2 lineas) < C++ (~8) < Java (~8) para la misma logica."},
        ],
    },
    # --- Curar 3 mas con la MISMA estructura (ver Step 2). ---
]
```

- [ ] **Step 2: Curar los otros 3 problemas en `PROBLEMAS`**

Agregar 3 dicts más a la lista, mismo formato, con código **comentado** real en los 3 lenguajes. Specs:

- **`celsius-fahrenheit`** — "Conversion Celsius a Fahrenheit" (nivel Basico). Idea: aplicar `F = C * 9/5 + 32`. Algoritmo en los 3: leer `c` (decimal/float), calcular, imprimir. Resaltar: C++ y Java usan `double`/`float`; Python no declara tipo; la division `9/5` en C++/Java con enteros trunca (usar `9.0/5`), en Python 3 `/` ya es decimal (punto a comentar). Diferencias: tipos numéricos, división entera vs real, I/O.
- **`factorial`** — "Factorial de un numero" (nivel Medio). Idea: `n! = 1*2*...*n` con un bucle. Algoritmo: leer `n`, acumular en un `for` de 1 a n, imprimir. Resaltar: el `for` en cada lenguaje (C++ `for(int i=1;i<=n;i++)`, Python `for i in range(1,n+1)`, Java igual que C++); el acumulador. Diferencias: sintaxis del for/range, tipos (long para no desbordar en C++/Java vs int ilimitado de Python — punto interesante a comentar).
- **`bubble-sort`** — "Ordenamiento burbuja (Bubble Sort)" (nivel Avanzado). Idea: comparar pares adyacentes e intercambiarlos hasta ordenar; dos bucles anidados. Algoritmo: arreglo fijo (ej. `{5,2,9,1}`), dos `for` anidados, swap condicional, imprimir el arreglo. Resaltar: arreglos (C++ `int a[]`/vector, Python lista, Java `int[]`), el swap (C++/Java con variable temporal o `std::swap`, Python `a[j],a[j+1]=a[j+1],a[j]` — destacar el swap pythónico), recorrer/imprimir. Diferencias: arreglos, swap, concisión de Python.

Cada uno con su `como` por lenguaje (1-2 frases) y 3-4 `diferencias`.

- [ ] **Step 3: Agregar el view `comparar` en `apps/ejercicios/views.py`**

Agregar el import al inicio (junto a los otros) y el view después de `inicio`:

```python
# (al inicio del archivo, junto a los imports existentes)
from .comparaciones import PROBLEMAS
```

```python
# (nuevo view, después de la función inicio)
def comparar(request):
    return render(request, 'comparaciones/comparar.html', {'problemas': PROBLEMAS})
```

- [ ] **Step 4: Agregar la ruta en `apps/ejercicios/urls.py`**

Dentro de `urlpatterns`, después de la línea de `inicio`:

```python
    path('comparar/', views.comparar, name='comparar'),
```

- [ ] **Step 5: Verificar la estructura por shell**

Run (desde `proyecto_django`):
```
python manage.py shell -c "from apps.ejercicios.comparaciones import PROBLEMAS; print('n=', len(PROBLEMAS)); [print(p['slug'], '->', [l['id'] for l in p['lenguajes']]) for p in PROBLEMAS]"
```
Expected: `n= 4` y cada problema con `['cpp', 'python', 'java']`.

- [ ] **Step 6: Commit**

```
git add apps/ejercicios/comparaciones.py apps/ejercicios/views.py apps/ejercicios/urls.py
git commit -m "feat(comparar): datos curados (4 problemas) + view + ruta /comparar/"
```

---

## Task 2: Template + CSS + JS

**Files:**
- Create: `templates/comparaciones/comparar.html`, `static/css/comparar.css`

- [ ] **Step 1: Crear `templates/comparaciones/comparar.html`**

```html
{% extends 'base.html' %}
{% load static %}
{% block titulo %}Comparar lenguajes{% endblock %}

{% block head_extra %}
<link rel="stylesheet" href="{% static 'css/comparar.css' %}">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/python.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/languages/java.min.js"></script>
{% endblock %}

{% block contenido %}
<section class="hero">
  <h1>Un problema, <span>tres lenguajes</span></h1>
  <p>Mira como el mismo algoritmo se resuelve en C++, Python y Java, y que cambia en cada uno.</p>
</section>

<div class="container" style="padding-top:1.5rem">

  <div class="comparar-tabs">
    {% for p in problemas %}
    <button type="button" class="comparar-tab{% if forloop.first %} active{% endif %}" data-slug="{{ p.slug }}">{{ p.titulo }}</button>
    {% endfor %}
  </div>

  {% for p in problemas %}
  <section class="comparar-problema{% if forloop.first %} active{% endif %}" data-slug="{{ p.slug }}">
    <div class="comparar-enunciado"><b>📝 Problema:</b> {{ p.enunciado }} <span class="chip chip-{{ p.nivel|lower }}">{{ p.nivel }}</span></div>
    <div class="comparar-idea">💭 <b>Idea:</b> {{ p.idea }}</div>

    <div class="comparar-grid">
      {% for l in p.lenguajes %}
      <div class="comparar-col">
        <div class="comparar-lang" style="background:{{ l.color }}">{{ l.label }}</div>
        <pre><code class="language-{{ l.id }}">{{ l.codigo }}</code></pre>
        <div class="comparar-como"><b>Como lo hace:</b> {{ l.como }}</div>
      </div>
      {% endfor %}
    </div>

    <div class="comparar-dif">
      <div class="dif-titulo">🔍 ¿Que cambia y por que?</div>
      {% for d in p.diferencias %}
      <div class="dif-item">• <b>{{ d.titulo }}:</b> {{ d.detalle }}</div>
      {% endfor %}
    </div>
  </section>
  {% endfor %}

</div>
{% endblock %}

{% block scripts %}
<script>
  document.querySelectorAll('.comparar-tab').forEach(function (tab) {
    tab.addEventListener('click', function () {
      var slug = tab.dataset.slug;
      document.querySelectorAll('.comparar-tab').forEach(function (t) { t.classList.toggle('active', t === tab); });
      document.querySelectorAll('.comparar-problema').forEach(function (s) { s.classList.toggle('active', s.dataset.slug === slug); });
    });
  });
</script>
{% endblock %}
```

> Nota: el `chip chip-{{ nivel|lower }}` reusa los chips de dificultad de `style.css` (`chip-basico/medio/avanzado`) — por eso el `nivel` se cura como "Basico"/"Medio"/"Avanzado". Django escapa el contenido de `{{ l.codigo }}`, así que el código se muestra literal; highlight.js (script de `base.html` sobre `pre code`) lo resalta usando los packs cpp/python/java.

- [ ] **Step 2: Crear `static/css/comparar.css`**

```css
/* comparar.css — pagina "Un problema, tres lenguajes" (claro + oscuro) */

.comparar-tabs { display: flex; gap: .5rem; flex-wrap: wrap; margin-bottom: 1.25rem; }
.comparar-tab {
  background: var(--surface); border: 1px solid var(--border); color: var(--text-muted);
  padding: .5rem 1rem; border-radius: 20px; font-family: 'Nunito', sans-serif;
  font-weight: 700; font-size: .9rem; cursor: pointer; transition: var(--transicion);
}
.comparar-tab:hover { border-color: var(--azul-claro); color: var(--text); }
.comparar-tab.active { background: var(--navbar-bg); color: #fff; border-color: var(--navbar-bg); }

.comparar-problema { display: none; }
.comparar-problema.active { display: block; animation: comparar-fade .25s ease; }
@keyframes comparar-fade { from { opacity: 0; } to { opacity: 1; } }

.comparar-enunciado {
  background: var(--naranja-suave); border-left: 4px solid var(--naranja); color: var(--text);
  padding: .7rem 1rem; border-radius: 8px; font-size: .95rem;
  display: flex; align-items: center; gap: .6rem; flex-wrap: wrap;
}
.comparar-idea { color: var(--text-muted); font-size: .9rem; margin: .6rem 0 1.1rem; line-height: 1.6; }

.comparar-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; }
.comparar-col { display: flex; flex-direction: column; }
.comparar-lang { color: #fff; font-weight: 700; font-size: .85rem; padding: .45rem .85rem; border-radius: 8px 8px 0 0; }
.comparar-col pre { margin: 0; background: #1e1e1e; padding: 1rem; overflow-x: auto; }
.comparar-col pre code { font-family: 'Fira Code', monospace; font-size: .8rem; line-height: 1.65; background: transparent; }
.comparar-como {
  background: var(--surface); border: 1px solid var(--border); border-top: none;
  border-radius: 0 0 8px 8px; padding: .7rem .85rem; font-size: .85rem; color: var(--text-muted);
}
.comparar-como b { color: var(--heading); }

.comparar-dif {
  background: var(--surface-2); border: 1px solid var(--border); border-radius: 8px;
  padding: 1rem 1.1rem; margin-top: 1.25rem; font-size: .9rem;
}
.comparar-dif .dif-titulo { font-weight: 800; color: var(--heading); margin-bottom: .5rem; }
.comparar-dif .dif-item { color: var(--text); margin-bottom: .35rem; line-height: 1.5; }

/* El callout naranja-suave es una isla clara en oscuro -> tinte translucido */
html[data-theme="dark"] .comparar-enunciado { background: rgba(244,137,31,.12); }

/* Responsivo: las 3 columnas se apilan (el pulido movil completo es el sub-proyecto 3) */
@media (max-width: 820px) {
  .comparar-grid { grid-template-columns: 1fr; }
}
```

- [ ] **Step 3: Reiniciar el server**

`preview_stop` + `preview_start name="logicweb"` (o reiniciar runserver). Necesario por `--noreload` (template nuevo).

- [ ] **Step 4: Verificar en el navegador (claro)**

Abrir `http://localhost:8000/comparar/`. Hard reload.
**Esperado:** hero "Un problema, tres lenguajes"; 4 tabs (Es par o impar / Celsius→Fahrenheit / Factorial / Bubble Sort); el primero activo muestra enunciado + idea + 3 columnas (C++/Python/Java) con código **resaltado** + "Cómo lo hace" + análisis de diferencias. Click en otra tab → cambia el problema.

- [ ] **Step 5: Verificar resaltado y oscuro**

- Confirmar que el código tiene colores en los 3 lenguajes (highlight.js cargó python/java). En consola: `hljs.listLanguages?.()` debería incluir cpp, python, java; o inspeccionar que los `<code>` tengan spans `.hljs-*`.
- Activar oscuro (`document.documentElement.dataset.theme='dark'` o toggle) + detector de islas:
```js
(() => { const bad=[]; for (const el of document.querySelectorAll('main *')) { const bg=getComputedStyle(el).backgroundColor; const m=bg.match(/rgba?\((\d+), (\d+), (\d+)(?:, ([\d.]+))?\)/); if(!m) continue; const r=+m[1],g=+m[2],b=+m[3],a=m[4]===undefined?1:+m[4]; if(a>0.5 && (r+g+b)/3>200) bad.push({cls:el.className,bg}); } return bad.length; })()
```
Expected: `0` (el bloque de código `#1e1e1e` no cuenta como isla; el callout naranja usa el override dark).

- [ ] **Step 6: Commit**

```
git add templates/comparaciones/comparar.html static/css/comparar.css
git commit -m "feat(comparar): template, tabs, 3 columnas y estilos (claro/oscuro)"
```

---

## Task 3: Enlazar chips del hero + verificación final

**Files:**
- Modify: `templates/inicio/index.html`

- [ ] **Step 1: Convertir los chips de lenguaje del hero en enlaces a `/comparar/`**

En `templates/inicio/index.html`, reemplazar el bloque `.hero-langs`:

```html
  <div class="hero-langs">
    <span class="lang-chip">⚡ C++</span>
    <span class="lang-chip">🐍 Python</span>
    <span class="lang-chip">☕ Java</span>
  </div>
```

por (los 3 chips enlazan a la comparación):

```html
  <div class="hero-langs">
    <a href="{% url 'comparar' %}" class="lang-chip">⚡ C++</a>
    <a href="{% url 'comparar' %}" class="lang-chip">🐍 Python</a>
    <a href="{% url 'comparar' %}" class="lang-chip">☕ Java</a>
  </div>
```

En `static/css/home.css`, asegurar que `.hero-langs .lang-chip` no se subraye como enlace (agregar `text-decoration:none; cursor:pointer;` a la regla existente):

```css
.hero-langs .lang-chip {
  background: rgba(255,255,255,.14);
  color: #fff;
  padding: .35rem .9rem;
  border-radius: 20px;
  font-size: .85rem;
  font-weight: 700;
  text-decoration: none;
  cursor: pointer;
  transition: var(--transicion);
}
.hero-langs .lang-chip:hover { background: rgba(244,137,31,.28); }
```

> Nota: los chips son `<a>` dentro de `<main>`, pero la regla `html[data-theme="dark"] main a:not(.btn)` les daría color azul; el `.hero-langs .lang-chip` tiene `color:#fff` con especificidad mayor (clase+clase = 0,2,0 vs 0,2,2)… **verificar en el Step 3** que el chip queda blanco en oscuro; si no, agregar `html[data-theme="dark"] .hero-langs .lang-chip { color:#fff; }`.

- [ ] **Step 2: Reiniciar server + verificar el enlace**

Reiniciar (template de inicio cambió). Abrir `/` y hacer click en un chip de lenguaje del hero → debe navegar a `/comparar/`.

- [ ] **Step 3: Barrido final**

- `python manage.py check` → `System check identified no issues`.
- `/comparar/` en **claro y oscuro**: 0 islas (detector del Task 2), tabs funcionan, código resaltado. Chips del hero blancos en oscuro (ver nota Step 1).
- **Móvil** (~390px): las 3 columnas se apilan a 1; cada bloque de código tiene scroll horizontal propio; la página no desborda (salvo el navbar, que es el sub-proyecto 3).
- Cero regresión en el resto de páginas.

- [ ] **Step 4: Commit final**

```
git add templates/inicio/index.html static/css/home.css
git commit -m "feat(comparar): enlazar los chips del hero a /comparar/"
```

---

## Definición de "Hecho"

- `/comparar/` muestra 4 problemas (tabs) con el mismo problema en C++/Python/Java, código comentado + "cómo lo hace" + análisis de diferencias.
- Código resaltado en los 3 lenguajes; tabs cambian de problema.
- Se ve bien en claro y oscuro (0 islas); los chips del hero llevan a la página.
- En móvil las columnas se apilan sin romper la página.
- `manage.py check` limpio; cero regresión. Commits en rama, sin pushear hasta el OK.
