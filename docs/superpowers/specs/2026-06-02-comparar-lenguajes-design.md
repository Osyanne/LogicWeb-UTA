# Comparar Lenguajes — "Un problema, tres lenguajes"

**Fecha:** 2026-06-02
**Estado:** Diseño aprobado — pendiente plan de implementación
**Sub-proyecto:** 4/5. Hereda el theming (modo oscuro) y el estilo de bloques de código (`codigo.css`).

## Objetivo

Página educativa que muestra el **mismo problema resuelto en C++, Python y Java lado a lado**, con
explicaciones, para que el estudiante vea las **diferencias concretas de sintaxis** sobre código real
(no teoría genérica). Contenido **curado** (no generado desde la BD).

## Por qué contenido curado (y no desde la BD)

Se evaluó relacionar los ejercicios existentes, pero la BD **no tiene tríos limpios**: solo "Conversión
Celsius→Fahrenheit" está en los 3 lenguajes; los títulos son inconsistentes ("Conversión Celsius a
Fahrenheit — C++" vs "Conversión **de** Celsius a Fahrenheit — Java"); muchos problemas están en 1-2
lenguajes. Relacionar sería frágil e incompleto. Por eso se **cura** contenido de calidad: 4 problemas
elegidos, con código + explicaciones escritos a mano.

## Contenido (4 problemas, de básico a avanzado)

1. **Es par o impar** — operador módulo + condicional.
2. **Conversión Celsius → Fahrenheit** — fórmula + entrada/salida.
3. **Factorial** — bucle (o recursión).
4. **Bubble Sort (ordenamiento burbuja)** — arreglos + bucles anidados.

Cada problema incluye: **enunciado**, **"💭 Idea"** (el concepto), y por lenguaje **código comentado** +
**"Cómo lo hace"** (un párrafo), más un **"🔍 ¿Qué cambia y por qué?"** (análisis en puntos: E/S, tipos,
estructura, concisión).

## Arquitectura

- **Datos** — `apps/ejercicios/comparaciones.py` (NUEVO): constante `PROBLEMAS`, lista de dicts con:
  `slug`, `titulo`, `enunciado`, `idea`, `lenguajes` (dict `cpp`/`python`/`java` → `{codigo, como}`),
  `diferencias` (lista de `{titulo, detalle}`). Separa el contenido curado de la presentación.
- **View** — `comparar(request)` en `apps/ejercicios/views.py`: pasa `PROBLEMAS` al contexto.
- **URL** — `/comparar/` (name `comparar`) en el urls de la app.
- **Template** — `templates/comparaciones/comparar.html` (NUEVO): hero + **tabs** (un botón por problema)
  + una **sección por problema** (visible solo la activa) con enunciado, idea, **3 columnas**
  (C++/Python/Java: código comentado + "cómo lo hace") y el análisis de diferencias.
- **CSS** — `static/css/comparar.css` (NUEVO): tabs, grid de 3 columnas, columnas que se apilan en móvil.
  Usa **variables semánticas** (claro+oscuro). Los bloques de código reusan el look de editor.
- **JS** — tab-switcher (mostrar/ocultar el problema activo) **inline** en el `{% block scripts %}` del
  template (simple, como las pistas de `interactivo.html`).
- **Acceso** — los chips de lenguaje del hero en `templates/inicio/index.html` (⚡ C++ / 🐍 Python /
  ☕ Java) se vuelven **enlaces a `/comparar/`**.
- **Resaltado** — `base.html` ya carga highlight.js core + `cpp.min.js`. `comparar.html` agrega en
  `{% block head_extra %}` los packs `python.min.js` y `java.min.js` (CDN cdnjs, misma versión 11.9.0).
  Los bloques `<code class="language-{cpp|python|java}">` se resaltan con el script ya existente en base.

## Claro y oscuro

`comparar.css` usa variables semánticas; los bloques de código ya son oscuros (estilo editor) en ambos
temas. No requiere overrides especiales más allá de superficies/textos semánticos.

## Alcance

Página nueva `/comparar/` + `comparaciones.py` + view + url + template + `comparar.css` + JS inline +
enlazar los chips del hero. **No** toca modelos, BD ni migraciones.

## Fuera de alcance (YAGNI)

- Generar la comparación desde la BD / relacionar ejercicios (curado estático para v1).
- Más de 4 problemas (se agregan luego editando `comparaciones.py`).
- Responsive a fondo (es el sub-proyecto 3): en móvil las 3 columnas se apilan a 1; el pulido móvil
  completo (incluida la navbar) se hace después. La página no debe romperse en angosto.

## Verificación

1. `python manage.py check` limpio; `runserver` desde `proyecto_django`.
2. `/comparar/` carga; las **tabs cambian** de problema (JS).
3. El **código se resalta** en los 3 lenguajes (highlight.js python/java cargan).
4. **Claro y oscuro** (reusar el detector de "islas claras"; cero islas).
5. Los **chips del hero** enlazan a `/comparar/`.
6. **Móvil**: las 3 columnas se apilan, sin desborde de la página.
7. Cero regresión en otras páginas.

## Riesgos / gotchas

- Confirmar que `python.min.js`/`java.min.js` de cdnjs cargan y resaltan (si fallara, los bloques quedan
  sin color pero legibles — degradación aceptable).
- `runserver --noreload`: reiniciar el server tras editar el template; cache-bust del CSS al verificar.
- El código curado debe ser **correcto y comparable** (mismo problema, estilo parejo entre lenguajes).
- Las 3 columnas de código en una pantalla angosta: asegurar `overflow-x` en cada bloque + apilado en móvil.
