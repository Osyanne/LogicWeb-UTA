# Spec — Notificaciones de logros (mejora 5/5)

**Fecha:** 2026-06-03
**Estado:** Aprobado (brainstorming)
**Sub-proyecto:** Pestaña/sistema de notificaciones — última de las 5 mejoras del usuario.

## 1. Objetivo

Dar al estudiante un **feed de notificaciones de logros**, generadas **automáticamente** por el
sistema cuando alcanza hitos de progreso. Cero intervención de un docente (el rol docente sigue
dormido). Refuerza la gamificación y es un punto fuerte para la defensa del proyecto.

Acceso vía **campanita 🔔 en el navbar** (con badge de no-leídas + dropdown de las últimas) y una
**página dedicada `/notificaciones/`** con el feed completo.

## 2. Alcance

**Dentro (v1):**
- 3 familias de logros: unidad completada, primeros pasos, volumen acumulado.
- Modelo `Notificacion` persistente, con deduplicación por logro.
- Generación automática enganchada al signal de `Intento` existente.
- Campanita + badge + dropdown en el navbar (solo autenticados).
- Página `/notificaciones/` con el feed completo; al abrirla marca todo como leído.
- Tests pytest (ataca de paso el `tests.py` vacío pendiente).

**Fuera (YAGNI):** rachas · galería de insignias coleccionables (los datos quedan listos para
hacerla después) · borrar notificaciones · marcar una sola como leída · email · tiempo real /
websockets · avisos del docente.

## 3. Arquitectura

Decisión clave: las notificaciones se **generan en un signal**, no en las vistas. El proyecto ya
usa `post_save` de `Intento` para recalcular `ProgresoEstudiante`; se añade un receiver hermano
para los logros. Beneficio: cero cambios en `views.py`, un único punto de evaluación, mismo patrón
que ya existe. `apps/ejercicios/apps.py` ya hace `ready() → import signals`, así que el nuevo
receiver se registra sin tocar `apps.py`.

```
Estudiante responde interactivo
        │
        ▼
  views (crea Intento)        ← SIN CAMBIOS
        │ post_save(created)
        ├──► actualizar_progreso_estudiante   (ya existe)
        └──► generar_notificaciones_logros     (NUEVO)
                 │ if created and resultado=='correcto'
                 ▼
            otorgar_logros(usuario, intento)   (apps/ejercicios/logros.py)
                 │ evalúa las 3 familias
                 ▼
            Notificacion.objects.get_or_create(usuario, clave, defaults={...})
                                                 └─ idempotente (dedup)
```

## 4. Modelo de datos — `Notificacion` (migración `0006`)

| Campo    | Tipo | Notas |
|----------|------|-------|
| usuario  | FK → Usuario (`related_name='notificaciones'`) | dueño |
| tipo     | CharField choices `unidad` / `primer_paso` / `volumen` | categoría/estilo |
| clave    | CharField(50) | id único del logro: `unidad_1`, `primer_java`, `volumen_25` |
| titulo   | CharField(150) | ej. "¡Dominaste la U1!" |
| mensaje  | TextField | texto descriptivo |
| icono    | CharField(8) | emoji (🏆 / 🌱 / 📈) |
| leida    | BooleanField(default=False) | controla el badge |
| fecha    | DateTimeField(auto_now_add=True) | orden + "hace X" |

```
Meta: unique_together = ('usuario', 'clave')   # un logro se otorga una sola vez (dedup a nivel BD)
      ordering = ['-fecha']
```

La deduplicación es por construcción: `get_or_create(usuario, clave, defaults=...)`. Reintentar un
ejercicio ya logrado no crea duplicados.

## 5. Catálogo de logros — `apps/ejercicios/logros.py`

`otorgar_logros(usuario, intento)` evalúa las 3 familias y hace `get_or_create` de lo que falte.
Se llama **solo en intentos correctos** (un intento incorrecto no puede desbloquear nada → guard en
el signal, eficiente).

### 🏆 Unidad completada — `unidad_<n>` (n = unidad del intento)
- **Condición:** el usuario tiene ≥1 intento correcto en **cada** ejercicio interactivo activo de la
  unidad. Es decir: el conjunto de ejercicios interactivos activos de la unidad ⊆ el conjunto de
  ejercicios de esa unidad con al menos un intento correcto del usuario.
- **Denominador:** `Ejercicio.objects.filter(tema__unidad=n, categoria='interactivo', activo=True)`.
  (Los "resueltos" solo se leen, no generan intentos → no cuentan.)
- **Guard:** si la unidad no tiene interactivos activos (total = 0), no se otorga.
- Solo se evalúa la unidad del intento actual (optimización).
- Título "¡Dominaste la U{n}!", mensaje con el nombre de la unidad, icono 🏆.

### 🌱 Primeros pasos
- `primer_correcto`: el usuario tiene ≥1 intento correcto (su primer acierto global).
- `primer_cpp` / `primer_python` / `primer_java`: primer intento correcto en un ejercicio de ese
  lenguaje. Título "¡Tu primer ejercicio en {C++/Python/Java}!", icono 🌱.

### 📈 Volumen acumulado — `volumen_<umbral>` (umbral ∈ {10, 25, 50})
- **Métrica:** cantidad de **ejercicios distintos** resueltos correctamente:
  `Intento.objects.filter(usuario=u, resultado='correcto').values('ejercicio').distinct().count()`.
  (Ejercicios distintos, no reintentos — para que el logro sea honesto.)
- Al cruzar cada umbral se otorga el correspondiente. Cada umbral una sola vez (vía clave). Si el
  conteo salta varios de golpe, se otorgan todos los cruzados.
- Título "Llegaste a {umbral} ejercicios correctos", icono 📈.

## 6. UI

### Context processor — `apps/ejercicios/context_processors.py`
`notificaciones(request)`: si `request.user.is_authenticated`, devuelve
`{'noti_no_leidas': <int>, 'noti_recientes': <últimas 5>}`. Es la forma Django limpia para datos que
el navbar (en `base.html`, presente en todas las páginas) necesita globalmente. Se registra en
`config/settings.py` → `TEMPLATES[OPTIONS][context_processors]`.

### Navbar — `templates/base.html`
Dentro de `.navbar-user`, en el bloque `{% if user.is_authenticated %}`, una campanita:
- Botón 🔔 + `<span class="noti-badge">` con `noti_no_leidas` (oculto si 0).
- **Dropdown** (oculto por defecto) con `noti_recientes`: icono + título + `{{ noti.fecha|timesince }}`,
  más un enlace "Ver todas" → `/notificaciones/`. Estado vacío si no hay.

### JS — `static/js/notificaciones.js`
Toggle del dropdown (abre/cierra al clic en la campanita, cierra al clic afuera / Escape). JS vanilla,
mismo enfoque que `theme.js`. Se añade al final de `base.html`.

### Página — `/notificaciones/`
- View `notificaciones` (login_required) en `apps/ejercicios/views.py`; ruta en `apps/ejercicios/urls.py`.
- Template `templates/notificaciones/lista.html` (extiende base): feed completo, cada item con icono +
  título + mensaje + "hace X". Estado vacío amable si no hay ninguna.
- **Al cargar (GET) marca todas las del usuario como leídas** (`...filter(usuario=u, leida=False).update(leida=True)`).

### CSS — `static/css/notificaciones.css`
Badge, dropdown e items del feed con **variables semánticas** (claro + oscuro gratis). Overrides
`html[data-theme="dark"]` solo si hace falta (badge/dropdown), siguiendo el patrón del modo oscuro ya
implementado.

## 7. Marcar leídas

Entrar a `/notificaciones/` marca todas como leídas → el badge baja a 0. Suficiente para v1; sin
endpoints de "marcar una sola". El dropdown refleja el estado actual sin mutarlo.

## 8. Testing (pytest)

- **`test_logros.py`**: cada familia se otorga cuando corresponde; **no se duplica** (llamar
  `otorgar_logros` dos veces ⇒ una sola `Notificacion`); unidad NO se otorga si falta 1 interactivo;
  volumen cuenta ejercicios distintos, no reintentos del mismo.
- **`test_signal_notificaciones.py`**: crear `Intento` correcto dispara las notificaciones esperadas;
  `Intento` incorrecto no crea ninguna.
- **`test_vista_notificaciones.py`**: la página marca leídas; el context processor devuelve el conteo
  correcto para un usuario autenticado y nada para anónimo.

## 9. Consideraciones operativas

- **Migración** `0006_notificacion`.
- **Navbar en móvil:** ya desborda en ~360px (sub-proyecto *responsive* pendiente). La campanita suma
  un elemento pequeño; no lo agrava de forma bloqueante y el fix (hamburguesa) se encarga después.
- **Cache de estáticos:** CSS/JS nuevos se cachean agresivo → verificar con Ctrl+F5 / `cache:'no-store'`.
- **Claro + oscuro:** verificar ambas en la campanita, dropdown y página (0 islas claras).
- **Prod (Render):** `build.sh` ya corre `collectstatic` + `migrate`; los estáticos nuevos y la
  migración se aplican solos en el deploy. WhiteNoise manifest OK.

## 10. Archivos afectados

**Nuevos:** `apps/ejercicios/logros.py` · `apps/ejercicios/context_processors.py` ·
`apps/ejercicios/migrations/0006_notificacion.py` · `templates/notificaciones/lista.html` ·
`static/css/notificaciones.css` · `static/js/notificaciones.js` · tests.

**Modificados:** `apps/ejercicios/models.py` (modelo) · `apps/ejercicios/signals.py` (receiver) ·
`apps/ejercicios/views.py` (view) · `apps/ejercicios/urls.py` (ruta) · `templates/base.html` (campanita
+ script) · `config/settings.py` (context processor).
