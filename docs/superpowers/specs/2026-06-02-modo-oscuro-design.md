# Modo Oscuro (OLED) — LogicWeb UTA

**Fecha:** 2026-06-02
**Estado:** Diseño aprobado — pendiente plan de implementación
**Sub-proyecto:** 1/5 del lote de mejoras (modo oscuro → rediseño inicio → responsive → comparar lenguajes → notificaciones)

## Objetivo

Agregar un modo oscuro estilo **OLED** a toda la app pública de LogicWeb UTA. Debe respetar la
preferencia del sistema operativo, permitir override manual persistente, y **no tocar la base de
datos**. En modo claro no debe haber ninguna regresión visual.

## Decisiones tomadas

- **Paleta:** Negro OLED — fondo `#000` puro, texto **casi-blanco** y superficies gris muy oscuro
  (evita el "halation"/vibración del texto en lecturas largas de teoría).
- **Activación:** respeta `prefers-color-scheme`; el toggle manual fija una preferencia explícita.
- **Persistencia:** `localStorage` (cliente). Sin cambios en BD.
- **Arquitectura:** capa de variables CSS **semánticas** (no redefinir las literales de marca).

## Arquitectura de theming

### Problema que resuelve
Hoy las variables son colores **literales** (`--blanco`, `--azul`, `--gris-fondo`) y algunas tienen
doble propósito: `--azul` es **fondo** de la navbar *y* **color de títulos**. En oscuro, un título en
`--azul` (#1a2744) quedaría invisible sobre una tarjeta oscura. Por eso se introduce una capa que
describe el **rol**, no el color.

### Capa semántica (nueva, en `:root` = modo claro por defecto)

| Variable | Rol | Claro | Oscuro (OLED) |
|---|---|---|---|
| `--bg` | fondo de página | `#f5f6fa` | `#000000` |
| `--surface` | tarjetas / paneles | `#ffffff` | `#121214` |
| `--surface-2` | cajas internas (ipo-box, header de código, pseudocódigo) | `#f5f6fa` | `#1b1b1f` |
| `--text` | texto principal | `#1c2135` | `#f0f0f2` |
| `--text-muted` | texto secundario | `#5a6478` | `#9a9aa3` |
| `--heading` | títulos (h1–h3 de secciones / cards) | `#1a2744` | `#f4f4f6` |
| `--border` | bordes y divisores | `#dde1ea` | `#2a2a30` |
| `--shadow` | sombra de tarjetas | `0 4px 20px rgba(26,39,68,.10)` | `0 4px 20px rgba(0,0,0,.5)` |
| `--shadow-hover` | sombra hover | `0 8px 32px rgba(26,39,68,.18)` | `0 8px 32px rgba(0,0,0,.6)` |
| `--navbar-bg` | fondo navbar / footer | `#1a2744` | `#0b1220` (azul-negro, guiño de marca) |
| `--accent` | naranja sólido (botones, bordes activos) | `#f4891f` | `#ff9a33` (un toque más vivo) |

Los acentos de marca se conservan en ambos temas: `--naranja`, `--verde-ok`, `--rojo-err`,
`--azul-claro`. Las variables `--radio`, `--transicion` no cambian.

### Bloque de modo oscuro
`html[data-theme="dark"] { ... }` redefine las semánticas a la columna "Oscuro".

### Migración de usos (mecánica, en los 4 CSS)
- `background: var(--blanco)` → `var(--surface)`
- `background: var(--gris-fondo)` → `var(--bg)` (body) o `var(--surface-2)` (cajas internas), según contexto
- `color: var(--texto)` → `var(--text)`
- `color: var(--texto-suave)` → `var(--text-muted)`
- `color: var(--azul)` **en títulos** → `var(--heading)` — **NO** cambiar donde `--azul` es fondo (navbar, botones, footer, thead de tablas)
- `var(--gris-borde)` y `var(--borde)` → `var(--border)` — esto además **arregla un bug latente**: `--borde` no existe en `:root`, así que hoy esos bordes salen transparentes
- `var(--sombra)` / `var(--sombra-hover)` → `var(--shadow)` / `var(--shadow-hover)`

### Elementos con color hardcodeado a adaptar en oscuro
- **style.css:** `.chip-*` y `.alert-info` (fondo pastel + texto saturado) → fondo `rgba()` translúcido del color + texto en versión clara.
- **codigo.css:** `.bloque-pseudo pre` (fondo `#f8f9fc`) → `var(--surface-2)`; `.aviso-cpp` (`#fff3e0` / `#5d3900`) → versión translúcida naranja sobre oscuro. Los bloques de código C++ (`.bloque-cpp` `#1e1e1e`, header `#2d2d2d`) **ya son oscuros → se mantienen**.
- **reportes.css:** `.progress-bar-wrap` / `.unidad-bar-wrap` (`#e0e0e0`) → `var(--surface-2)`; `.tabla-historial tbody tr:hover` (`#f5f7ff`) → superficie oscura; `.badge-correcto` / `.badge-incorrecto` → `rgba()` translúcido + texto claro.

### Mapeo de chips/badges en oscuro (referencia de valores)
- resuelto (azul): `bg rgba(59,130,246,.16)` / texto `#7db3ff`
- interactivo (morado): `bg rgba(168,85,247,.16)` / texto `#c89bf5`
- básico (verde): `bg rgba(46,160,67,.16)` / texto `#6ee7a0`
- medio (ámbar): `bg rgba(245,158,11,.16)` / texto `#fbbf24`
- avanzado (rosa): `bg rgba(236,72,153,.16)` / texto `#f49ac2`
- correcto: `bg rgba(46,160,67,.12)` / texto `#6ee7a0`
- incorrecto: `bg rgba(239,68,68,.14)` / texto `#ff8a8a`

## Comportamiento (toggle + persistencia)

### Inicialización anti-FOUC
Script **inline en el `<head>`** de `base.html`, antes de que se pinte el body. Lee
`localStorage.theme`; si no existe, usa `matchMedia('(prefers-color-scheme: dark)')`; aplica
`document.documentElement.dataset.theme`. Sin esto habría un flashazo blanco al recargar en oscuro.

### Toggle
- `<button>` accesible (`aria-label`, `aria-pressed`) en la navbar, con ícono ☀️/🌙.
- `static/js/theme.js`: al click alterna el tema, guarda en `localStorage`, actualiza ícono y `aria`.
- Escucha cambios del sistema (`matchMedia` change) **solo si** el usuario no fijó preferencia manual.

### Prioridad de resolución
`localStorage.theme` (`'dark'` | `'light'`) > `prefers-color-scheme` > `'light'`.

## Alcance

Toda la app pública: navbar, footer, home, teoría (ruta + detalle), listas (resueltos /
interactivos), detalle / interactivo, retroalimentación (ok + err), reportes, login, registro.
**Excluido:** `/admin/` (Django ya trae su propio modo oscuro).

## Archivos afectados

- `static/css/style.css` — capa semántica + bloque `[data-theme=dark]` + chips/alerts + migración.
- `static/css/codigo.css` — migración + pseudocódigo + aviso educativo.
- `static/css/contenidos.css` — migración + fix `--borde`.
- `static/css/reportes.css` — migración + barras + badges + fix `--borde`.
- `templates/base.html` — script anti-FOUC en `<head>` + botón toggle en navbar.
- `static/js/theme.js` — **NUEVO**.

## Fuera de alcance (YAGNI)

- Cambios en modelos / migraciones / BD.
- Persistencia por usuario en BD (diferido; `localStorage` cubre v1).
- Tests automatizados nuevos (`tests.py` sigue vacío; la verificación visual cubre v1).
- El rediseño de la home (es el sub-proyecto 2).

## Verificación

1. `python manage.py runserver` **desde `proyecto_django`** (ojo: hay un `manage.py` huérfano en el home que secuestra el comando).
2. Preview / Playwright en **claro y oscuro**, sin caché (`cache:no-store` / `Ctrl+F5` — gotcha conocido de CSS cacheado).
3. Recorrer páginas clave en ambos temas: home, teoría (ruta + detalle), lista resueltos, lista interactivos, detalle interactivo, retroalimentación ok/err, reportes, login, registro.
4. Checklist por página: ¿texto legible? ¿islas claras? ¿chips/badges con contraste? ¿bordes visibles?
5. Contraste AA del texto principal (`#f0f0f2` sobre `#000` / `#121214`).
6. Recargar en oscuro → **cero flash blanco**.
7. Toggle: alterna, persiste tras reload, y refleja el sistema en la primera visita.

## Riesgos / gotchas

- **Cache agresivo de CSS** en local → `Ctrl+F5`. En prod, WhiteNoise con manifest-hash rompe caché solo.
- **Cero regresión en claro:** las semánticas en modo claro deben igualar exactamente los valores actuales.
- `prefers-color-scheme` se prueba en Playwright con `emulateMedia`.
