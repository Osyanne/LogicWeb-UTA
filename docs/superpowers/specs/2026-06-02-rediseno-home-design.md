# Rediseño de la Home — LogicWeb UTA

**Fecha:** 2026-06-02
**Estado:** Diseño aprobado — pendiente plan de implementación
**Sub-proyecto:** 2/5 (rediseño de inicio). Hereda el theming del modo oscuro (sub-proyecto 1, ya en producción).

## Objetivo

Rediseñar la página de inicio para que sea **moderna e informativa SIN duplicar** la navegación que
ya hacen el navbar y las pestañas (Teoría / Resueltos / Práctica). La home deja de ser un "segundo
índice" y pasa a ser una **portada que engancha**: bienvenida + orientación + un gancho al contenido.

## Decisiones tomadas

- Dirección visual: **"Clásica Plus / Portada que engancha"** (evolución pulida de la home actual).
- El **título del hero se mantiene**: "Bienvenido a **LogicWeb UTA**" (LogicWeb UTA en naranja).
- **Se QUITAN** (eran redundantes con navbar/Teoría): la tira de badges de unidades (`.unidades-strip`)
  y el grid de 4 accesos `.accesos-grid` ("¿Qué quieres hacer hoy?").
- **Se AGREGAN**: chips de lenguaje en el hero, sección "¿Cómo funciona?" (3 pasos), sección
  "Ejercicios destacados" (1 por lenguaje, como gancho), banner de estadísticas.
- Funciona en **claro y oscuro** reusando las variables semánticas del modo oscuro.

## Estructura de la home (orden final)

1. **Hero** — título + subtítulo (los actuales) + CTAs + 3 chips de lenguaje.
   - No autenticado: botones "🚀 Crear mi cuenta" (naranja) + "Ingresar" (outline).
   - Autenticado: botón "⚙️ Practicar ahora".
   - Chips: ⚡ C++ · 🐍 Python · ☕ Java (debajo de los botones).
2. **¿Cómo funciona?** — 3 pasos, contenido estático:
   - 📚 **1 · Estudia la teoría** — Lógica, algoritmos y POO por unidad.
   - ⚙️ **2 · Practica** — Analiza código y responde, con pistas.
   - 📊 **3 · Mide tu avance** — Aciertos, errores y progreso por unidad.
3. **Ejercicios destacados** ("Date una idea") — 3 cards, **una por lenguaje**. Cada card: chip de
   lenguaje + chip de dificultad + título + enunciado corto (truncado), enlazada a su detalle.
   Encabezado de sección con un enlace **"Ver todos →"** a la lista de resueltos.
4. **Banner de stats** — nº de ejercicios · nº de unidades · nº de lenguajes (3).

## Backend — `apps/ejercicios/views.py::inicio`

Reemplaza el contexto actual (`unidades`, `total_ejercicios`) por:

- `total_ejercicios` = `Ejercicio.objects.filter(activo=True).count()` (igual que hoy).
- `num_unidades` = `Tema.objects.values('unidad').distinct().count()` (para el stat; hoy 4).
- `destacados` = lista de hasta 3 ejercicios, **uno por lenguaje** (`cpp`, `python`, `java`). Para cada
  lenguaje: el primer ejercicio `activo=True`, **prefiriendo `categoria='resuelto'`** (mejor vitrina);
  si no hay resuelto de ese lenguaje, cae a cualquiera activo de ese lenguaje; si no hay ninguno, se
  omite. Usar `select_related('tema')`. Degrada con gracia (puede haber menos de 3).
- Se elimina `unidades` del contexto (ya no se usa la strip).

Modelos: `Ejercicio(titulo, enunciado, lenguaje['cpp'|'python'|'java'], dificultad, categoria['resuelto'|'interactivo'], tema FK, activo, pk, get_dificultad_display)`, `Tema(unidad, nombre_tema)`.

## Frontend

- **`templates/inicio/index.html`** — reescribir con las 4 secciones. Quitar `.unidades-strip` y
  `.accesos-grid`. Cargar el CSS nuevo en `{% block head_extra %}`. Los destacados iteran `destacados`
  y cada card enlaza según `categoria`: `resuelto_detalle` o `interactivo_detalle` (mismo patrón que
  `lista_resueltos.html`). Los chips de lenguaje usan el mismo markup/colores que las listas
  (C++ `#00599c`, Python `#3572A5`, Java `#b07219`).
- **`static/css/home.css`** *(NUEVO)* — clases nuevas: `.hero-langs` (chips del hero),
  `.como-funciona` + `.pasos-grid` + `.paso-card`, `.destacados-grid` + `.card-destacado`,
  `.stats-banner`. **Debe usar variables semánticas** (`--surface`, `--text`, `--text-muted`,
  `--heading`, `--border`, `--shadow`) para verse bien en claro y oscuro sin overrides extra.
  Reutiliza `.hero`, `.container`, `.btn*`, `.chip*`, `.section-title` de `style.css`.

## Alcance

Solo la home: `templates/inicio/index.html`, `static/css/home.css` (nuevo) y el view `inicio`.
**No** se tocan otras páginas, modelos ni migraciones.

## Fuera de alcance (YAGNI)

- Versión "dashboard" para logueados (retomar / progreso): se evaluó y se descartó para v1 (encaja con
  el futuro sub-proyecto "favoritos / retomar").
- Animaciones complejas: solo micro-transiciones con las variables existentes (y `prefers-reduced-motion`
  ya es global desde el modo oscuro).
- Cambios en navbar o en Teoría.
- Responsive a fondo (es el sub-proyecto 3): la home nueva NO debe romperse en pantalla angosta, pero
  el pulido móvil completo se hace después.

## Verificación

1. `python manage.py check` sin errores; `runserver` desde `proyecto_django`.
2. Preview/Playwright en **claro y oscuro** (reusar el detector de "islas claras"; cero islas).
3. **Logueado y no autenticado** (los CTA del hero cambian; los destacados se ven igual).
4. Las cards de destacados enlazan al detalle correcto según categoría.
5. La home no se rompe en ancho de móvil (grids colapsan razonablemente).
6. Cero regresión: las demás páginas intactas.

## Riesgos / gotchas (heredados del modo oscuro)

- `runserver --noreload` cachea templates en memoria → **reiniciar el server** tras editar `index.html`.
- CSS nuevo: el browser cachea agresivo → cache-bust `?v=` / Ctrl+F5 al verificar.
- Las secciones nuevas **deben usar variables semánticas** (no literales `--blanco/--texto/--azul`)
  para no romper el modo oscuro.
- Destacados: degradar con gracia si falta algún lenguaje/categoría (no asumir que siempre hay 3).
