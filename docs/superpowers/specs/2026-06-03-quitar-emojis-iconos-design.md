# Spec — Reemplazar emojis por íconos SVG (look profesional)

- **Fecha:** 2026-06-03
- **Rama:** `feat/paralelo-chat` (worktree, base `origin/main` = 8c8fd8f)
- **Estado:** Aprobado el diseño visual; pendiente revisión del spec.

## Problema

La UI usa ~79 emojis decorativos en títulos, botones, navbar y badges. Le restan
seriedad a una plataforma educativa universitaria y dan la sensación de "hecho por IA".

## Objetivo

Aplicar una **política híbrida**: íconos SVG de línea (estilo Lucide/Feather) solo
donde aportan jerarquía; texto limpio en botones y sub-etiquetas; color para lenguajes
y unidades. Los íconos usan `stroke: currentColor`, así que se adaptan solos a claro/oscuro.

## Política aprobada

| Categoría | Hoy | Queda como |
|---|---|---|
| Marca (navbar) | 🎓 | ícono `code` (`</>`) naranja + "LogicWeb UTA" |
| Nombre de usuario (navbar) | 👤 | texto solo |
| Títulos de sección (h1/h2) | 📊 📚 🔑 🛤️ ⚙️ 💡 | ícono SVG + título |
| Botones y enlaces | 🚀 📥 📋 💡 ⚙️ | texto solo |
| Estado (acierto/error/aviso) | ✅ ❌ ⚠️ 🎉 ✗ | check-circle / x-circle / alert-triangle SVG, en color |
| Lenguajes | 🐍 ☕ ⚡ | punto de color de marca + nombre |
| Pasos del home (Estudia/Practica/Mide) | 📚 ⚙️ 📊 | números `1·2·3` en el círculo |
| Unidades 1-4 (Teoría) | 🧠 ⚙️ 🧩 📦 | `U1`–`U4` con el color de cada unidad |
| Sub-etiquetas (Idea/Problema/Teoría/Entrada/Proceso/Salida/Pseudocódigo/★) | 💭 🔍 📝 📖 📥 📤 ★ | texto en negrita (sin ícono) |
| Chips de tipo (Interactivo/Resuelto) | ⚙️ 📘 | texto plano (sin emoji) |
| Toggle de tema | 🌙 / ☀️ | ícono sol/luna SVG |
| Botón limpiar filtro | ✕ | ícono `x` SVG (o `×` tipográfico) |

**Regla de oro:** íconos SVG solo en marca, títulos, estado y toggle. Texto limpio en
botones y sub-etiquetas. Color (no emoji) para lenguajes y unidades.

## Inventario de íconos SVG (distintos)

Set monocromático de línea, 24×24, `stroke-width:2`, `fill:none`, `currentColor`:

`code`, `bar-chart`, `layers`, `log-in`, `user-plus`, `route`, `terminal`,
`book-open`, `book`, `check-circle`, `x-circle`, `alert-triangle`, `x`, `sun`, `moon`.

Mapeo título → ícono (principales): Mi Progreso → `bar-chart`; Progreso por Unidad →
`layers`; Iniciar Sesión → `log-in`; Crear mi cuenta → `user-plus`; Ruta de Aprendizaje →
`route`; Práctica Interactiva → `terminal`; Ejercicios Resueltos → `book-open`;
Teoría de la unidad → `book`; avisos educativos → `alert-triangle`.

## Enfoque de implementación

1. **Partials de íconos** en `templates/icons/<nombre>.svg` (HTML inline). Se usan con
   `{% include "icons/bar-chart.svg" %}`, opcionalmente con `{% include ... with cls="ico ok" %}`.
   Una sola fuente de verdad por ícono; sin código Python; sin migraciones.
2. **CSS** nuevo en `style.css`: clase `.ico` (tamaño/alineación), variantes `.ico-sm`/`.ico-lg`,
   `.lang-dot` (punto de color), `.unidad-badge` (U1-U4 con color por unidad), número de paso.
3. **Lenguajes**: en `comparaciones.py` los labels pasan de `"⚡ C++"` a `"C++"`; el template
   pinta el punto con el campo `color` que ya existe en los datos. En chips/filtros de los
   templates, el punto de color se arma con la clase de lenguaje existente.
4. **Toggle de tema**: en `theme.js`, `SUN`/`MOON` pasan de emoji a string SVG inline.
5. **Pasos del home**: el `.paso-icono` muestra el número (1·2·3) en vez del emoji.
6. **Unidades**: el bloque `{% if tema.unidad == 1 %}…` pasa de emoji a badge `U1`–`U4`
   con la clase de color por unidad (azul/naranja/verde/magenta ya existentes).

## Modo claro/oscuro

Los íconos heredan `currentColor`, por lo que toman el color del texto del contexto
(títulos `--heading`, estado verde/rojo, marca naranja, botones blanco). Cero CSS extra
por tema. Verificado el principio en el mockup de brainstorming.

## Alcance

**Incluye** (15 templates + 3 archivos):
`base.html`, `inicio/index.html`, `usuarios/{login,registro}.html`,
`contenidos/{lista,detalle}.html`, `comparaciones/comparar.html`,
`retroalimentacion/respuesta.html`, `reportes/mi_progreso.html`,
`ejercicios/{interactivo,resuelto,lista_resueltos,lista_interactivos}.html`,
`static/css/style.css`, `static/js/theme.js`, `apps/ejercicios/comparaciones.py`,
y los nuevos `templates/icons/*.svg`.

**Excluye:**
- `apps/ejercicios/admin.py` (el `⚠️` está en un `help_text` interno del admin de Django,
  no es la página pública; **además ese archivo lo está editando el otro chat** —
  notificaciones — así que lo dejamos fuera para evitar conflictos).
- Cualquier cambio de modelos/migraciones (esto es solo templates/CSS/JS/datos).

## Coordinación con el chat paralelo (notificaciones)

- **Sin riesgo de migraciones**: este trabajo no toca `models.py` ni crea migraciones.
- **Posible solape textual** solo en `base.html` (si notificaciones agrega un ítem de
  navbar). Es un merge limpio y acotado, resoluble a mano; no hay stomping (worktrees).
- `comparaciones.py` y `style.css`: improbable que el otro chat los toque.

## Verificación

1. `python manage.py check` limpio.
2. Verificación visual con Playwright en **claro y oscuro** de las páginas clave
   (inicio, mi_progreso, comparar, interactivo, resuelto, login, teoría).
3. **Test de regresión**: un test que escanea los templates incluidos y falla si queda
   algún emoji decorativo (rango pictográfico). Deja la política como invariante permanente.
4. Confirmar que los íconos dibujados a mano se ven correctos (ya validados en el mockup).

## No-objetivos

- No rediseñar layouts ni cambiar la paleta.
- No agregar una librería de íconos externa (los SVG van inline, MIT-equivalentes propios).
- No tocar el panel de administración de Django.
