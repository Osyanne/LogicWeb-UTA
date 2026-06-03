# Login con identidad UTA + cuenta demo — Diseño

**Fecha:** 2026-06-03
**Rama:** `feat/login-identidad-uta` (worktree aislado, base `main` = `8c8fd8f`)
**Mejora:** idea #1 (cuenta demo visible) + idea #2 (login con identidad UTA) de la revisión competitiva del 2026-06-03.

## Problema

La pantalla de login actual (`templates/usuarios/login.html`) es una card genérica sin identidad: un `<h2>🔑 Iniciar Sesión</h2>` y los campos del form dentro de `base.html` (con navbar). La app del otro grupo gana en la primera impresión: login inmersivo con identidad institucional + credenciales demo visibles (el evaluador entra en 2 segundos). Queremos cerrar ese gap.

## Objetivos

1. Login (y registro) como **puerta institucional inmersiva**: pantalla propia, sin navbar, que comunique "Universidad Técnica de Ambato / LogicWeb UTA".
2. **Cuenta demo visible** y de 1 clic, para la defensa.
3. **Coherencia total** con la paleta existente de la app (navy + naranja). La identidad UTA la dan el **escudo + el texto institucional**, no un color nuevo.
4. **Aislamiento**: cero impacto en el resto del sitio y cero colisión con los otros 2 chats activos (notificaciones, quitar-emojis).

## No-objetivos (YAGNI)

- Rebrand de toda la app a rojo/granate UTA (los colores oficiales son blanco + rojo, pero migrar todo el sitio es un proyecto aparte y choca con los chats en curso).
- Login por email (la app entra por **username** vía `AuthenticationForm`; no se cambia).
- Foto real del campus de fondo (se evita por derechos; se reemplaza con motivo de código + paleta).
- Modo oscuro del login (la puerta es siempre la piel navy institucional).

## Decisiones de diseño

| Decisión | Elección | Por qué |
|---|---|---|
| Paleta | **Navy `#1a2744` + naranja `#f4891f` + blanco** (la de la app) | Coherencia con el sitio; el rojo UTA real haría incoherente el interior azul → se descartó. |
| Identidad UTA | Escudo + "Universidad Técnica de Ambato" | Da lo institucional sin depender del color. |
| Layout | **Split panel**: panel de marca navy a la izquierda + form a la derecha | Llena la pantalla (no queda vacío), y el panel vende value props al evaluador. |
| Estructura | Shell standalone `base_auth.html` (sin navbar/footer) | Aísla login/registro del resto; no toca `base.html` (que editan los otros chats). |
| Estilos | `auth.css` nuevo, reusa los tokens de `style.css` | DRY + coherente; si la paleta de la app cambia, el login la sigue. |
| Cuenta demo | username `demo` / `Demo123*`, sembrada por management command idempotente | Visible + autofill; reproducible en local y en Render. |

## Detalle visual (split panel)

**Panel izquierdo (≈45%, navy):**
- Fondo: gradiente navy (`#131d33 → #1a2744 → #2c4470`) + motivo de código tenue (`{ } </> ; () => []` en `rgba(255,255,255,.06)`, Fira Code).
- Escudo UTA (≈64px, aro naranja) + "Logic**Web** UTA" (Web en naranja, igual que el navbar-brand) + overline "UNIVERSIDAD TÉCNICA DE AMBATO".
- Value props: `▸ C++ · Python · Java`, `▸ Práctica con pistas`, `▸ Seguí tu progreso`.

**Lado derecho (≈55%, claro):**
- Card blanca con sombra (o panel directo): título "Iniciar Sesión".
- Campos `username` + `password` del `AuthenticationForm` (labels "Usuario" / "Contraseña"), estilizados.
- Botón primario navy (`linear-gradient(#1a2744,#243659)`) "Ingresar al sistema".
- Alert de error estilizado (credenciales inválidas).
- **Caja demo**: borde dashed naranja + fondo crema (`#fff6ea`), "Cuenta de demostración — Usuario: **demo** · Contraseña: **Demo123\***" + botón naranja "**Usar credenciales demo →**" (autofill).
- Footer: "¿No tienes cuenta? **Regístrate aquí**".

**Responsive:** en móvil el split se apila (panel arriba, form abajo); el panel se compacta.

## Arquitectura / Archivos

**Nuevos** (cero colisión con otros chats):
- `templates/base_auth.html` — shell pre-auth: `<head>` con `style.css` (tokens/fonts) + `auth.css`; `<body>` con el layout split; `{% block auth_content %}` + render de `messages`. Sin navbar, footer, theme-toggle, highlight.js ni theme.js. Sin script anti-flash (login siempre claro/navy).
- `static/css/auth.css` — estilo del split panel, la card, los campos, la caja demo, el motivo de código y el responsive. Usa `var(--navbar-bg)`, `var(--accent)`, `var(--heading)`, `var(--surface)`, etc.
- `static/img/uta-escudo.svg` (o `.png`) — escudo oficial UTA si se consigue; si no, monograma SVG limpio (navy/dorado).
- `apps/usuarios/management/__init__.py`, `apps/usuarios/management/commands/__init__.py`, `apps/usuarios/management/commands/crear_demo.py` — command idempotente.

**Reescritos** (solo 2; se entregan sin emojis, alineado con el chat de emojis):
- `templates/usuarios/login.html` — `{% extends 'base_auth.html' %}`, panel + form + caja demo + `<script>` inline de autofill (`id_username`/`id_password`). Preserva `?next=`.
- `templates/usuarios/registro.html` — mismo shell `base_auth.html`, look institucional (form de `RegistroForm`).

**Tocado mínimamente** (1 línea, al final, coordinado):
- `build.sh` — agregar `python manage.py crear_demo` tras `migrate` (para que el demo exista en Render).

**Sin cambios:** `apps/usuarios/views.py`, `forms.py`, `urls.py` (el `login_view` ya usa `AuthenticationForm` por username).

## Cuenta demo — `crear_demo`

Command idempotente (seguro de correr múltiples veces):
1. `get_or_create` de `Usuario(username='demo')` con `rol='estudiante'`, nombre "Estudiante Demo", email `demo@uta.edu.ec`; setea password `Demo123*` solo si se crea.
2. Siembra ~3-5 `Intento` correctos en ejercicios existentes (resiliente a PKs faltantes) → el signal `post_save` de `Intento` actualiza `ProgresoEstudiante`, así "Mi Progreso" no sale vacío en la demo.
3. Idempotencia: si el demo ya existe, no duplica intentos (chequear antes de sembrar).

Se ejecuta: en local una vez; en Render vía `build.sh` en cada deploy (idempotente).

## Aislamiento / trabajo en paralelo (3 chats)

- Todo el trabajo vive en el **worktree** `feat/login-identidad-uta` (base `main`), separado de `feat/notificaciones` (Chat B, working dir home) y `feat/paralelo-chat` (Chat C, emojis).
- Archivos nuevos = sin colisión. Los 2 templates reescritos: pedir al chat de emojis **no tocar** `login.html`/`registro.html` (acá ya salen sin emojis). `build.sh`: 1 línea, al final, merge al cierre.
- Merge a `main` por PR (o directo, a elección del user) tras verificación. Sin `Co-Authored-By`.

## Testing / verificación

- `python manage.py check` limpio.
- `crear_demo` idempotente: correr 2× no duplica usuario ni intentos.
- Playwright (browser real, no el preview que se cuelga con highlight.js):
  - `/login/` renderiza el split panel (claro), escudo y value props visibles.
  - Botón "Usar credenciales demo" autocompleta usuario/contraseña.
  - Login con `demo`/`Demo123*` → redirige a `inicio` (sesión iniciada).
  - `/registro/` hereda el shell institucional.
  - Responsive ~360px: el split se apila, sin overflow horizontal.
  - Estado de error (credenciales malas) se ve correcto.

## Riesgos

- **Escudo:** si no se consigue el oficial, fallback a monograma SVG (no bloquea).
- **`build.sh`:** único archivo compartido; coordinar el merge para no pisar otros cambios.
- **Postgres free de Render** expira ~90 días (riesgo preexistente del proyecto, no de esta feature).
