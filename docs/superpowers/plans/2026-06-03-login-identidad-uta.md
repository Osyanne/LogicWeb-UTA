# Login con identidad UTA + cuenta demo — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rediseñar las pantallas de login y registro como una "puerta institucional" inmersiva (split panel, identidad UTA por escudo + texto, paleta navy/naranja de la app) y agregar una cuenta demo visible de 1 clic.

**Architecture:** Shell standalone `base_auth.html` (sin navbar/footer) que carga `style.css` (tokens) + `auth.css` (layout inmersivo). El panel de marca izquierdo vive en el shell; login/registro solo llenan la card derecha vía `{% block auth_content %}`. La cuenta demo se siembra con un management command idempotente cuyos `Intento` disparan el signal que actualiza `ProgresoEstudiante`.

**Tech Stack:** Django 6.0, plantillas Django, CSS3 (variables semánticas + Flexbox), Store `python.exe` sin venv, Playwright MCP para verificación.

---

## Setup (worktree)

- Working dir: `C:/Users/osyanne/.config/superpowers/worktrees/proyecto_django/login-identidad-uta`
- Rama: `feat/login-identidad-uta` (base `main` = `8c8fd8f`).
- Correr Django **siempre desde el dir del worktree** (no desde el home — hay un `manage.py` huérfano ahí). El proyecto usa el paquete `config`, Store `python.exe` 3.13 + Django 6.0.4 sin venv.
- `db.sqlite3` está gitignored: el worktree arranca sin BD. La BD local se crea en la Task 7.
- Commits sin `Co-Authored-By`.

---

## File Structure

| Archivo | Acción | Responsabilidad |
|---|---|---|
| `static/img/uta-escudo.svg` | crear | Monograma/escudo UTA (navy + aro naranja). |
| `static/css/auth.css` | crear | Layout inmersivo: wrap, panel de marca, card, caja demo, motivo de código, responsive. Reusa tokens y `.btn`/`.form-group`/`.alert` de `style.css`. |
| `templates/base_auth.html` | crear | Shell pre-auth: `<head>` (style.css + auth.css), `.auth-wrap` (panel de marca + `{% block auth_content %}`), `messages`. Sin navbar/footer/JS. |
| `templates/usuarios/login.html` | reescribir | Extiende `base_auth`; card con form (username/password) + caja demo + script autofill. Sin emojis. |
| `templates/usuarios/registro.html` | reescribir | Extiende `base_auth`; card con `RegistroForm`. Sin emojis. |
| `apps/ejercicios/management/commands/crear_demo.py` | crear | Command idempotente: cuenta demo + siembra de intentos correctos. |
| `apps/ejercicios/management/__init__.py`, `.../commands/__init__.py` | crear | Paquetes vacíos para que Django descubra el command. |
| `apps/ejercicios/tests.py` | reescribir (está vacío) | Test del command (idempotencia + progreso). |
| `build.sh` | modificar | +1 línea: `python manage.py crear_demo` tras `loaddata`. |

No se tocan `views.py`, `forms.py`, `urls.py` (el `login_view` ya entra por username vía `AuthenticationForm`).

---

## Task 1: Escudo SVG

**Files:**
- Create: `static/img/uta-escudo.svg`

- [ ] **Step 1: Crear el SVG**

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" role="img" aria-label="Escudo LogicWeb UTA">
  <defs>
    <linearGradient id="uta-bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#3a5998"/>
      <stop offset="1" stop-color="#1a2744"/>
    </linearGradient>
  </defs>
  <circle cx="50" cy="50" r="46" fill="url(#uta-bg)" stroke="#f4891f" stroke-width="4"/>
  <circle cx="50" cy="50" r="38" fill="none" stroke="#f4891f" stroke-width="1" opacity="0.5"/>
  <text x="50" y="46" text-anchor="middle" font-family="Nunito, Segoe UI, sans-serif" font-size="25" font-weight="800" fill="#ffffff" letter-spacing="1">UTA</text>
  <text x="50" y="62" text-anchor="middle" font-family="Nunito, Segoe UI, sans-serif" font-size="6.5" font-weight="700" fill="#f4891f" letter-spacing="1.4">LOGICWEB</text>
</svg>
```

- [ ] **Step 2: Verificar que es SVG válido**

Run: `python -c "import xml.dom.minidom as m; m.parse('static/img/uta-escudo.svg'); print('SVG OK')"`
Expected: `SVG OK`

- [ ] **Step 3: Commit**

```bash
git add static/img/uta-escudo.svg
git commit -m "feat(login): escudo SVG monograma UTA para la puerta de acceso"
```

> Nota: si más adelante se consigue el escudo oficial en PNG, reemplazar el archivo manteniendo el nombre o actualizar el `{% static %}` en `base_auth.html`.

---

## Task 2: `auth.css` (layout inmersivo)

**Files:**
- Create: `static/css/auth.css`

- [ ] **Step 1: Crear el CSS completo**

```css
/* ═══════════════════════════════════════════════════════
   auth.css — LogicWeb UTA · pantallas de acceso (login/registro)
   Layout inmersivo "puerta institucional" (split panel).
   Reusa tokens y componentes de style.css (.btn, .form-group, .alert).
   ═══════════════════════════════════════════════════════ */

.auth-wrap {
  display: flex;
  min-height: 100vh;
}

/* ── Panel de marca (izquierda) ── */
.auth-panel {
  flex: 0 0 44%;
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2.5rem;
  color: #fff;
  background: linear-gradient(150deg, #131d33 0%, var(--azul) 48%, #2c4470 100%);
}
.auth-code-motif {
  position: absolute;
  inset: 0;
  padding: 1rem;
  font-family: 'Fira Code', monospace;
  font-size: 2.4rem;
  font-weight: 700;
  line-height: 2.4;
  letter-spacing: .3rem;
  color: rgba(255, 255, 255, .05);
  word-break: break-word;
  pointer-events: none;
  user-select: none;
}
.auth-brand { position: relative; max-width: 320px; }
.auth-escudo { width: 76px; height: 76px; margin-bottom: 1rem; }
.auth-overline {
  font-size: .72rem;
  font-weight: 800;
  letter-spacing: 1.6px;
  text-transform: uppercase;
  color: rgba(255, 255, 255, .85);
}
.auth-logo { font-size: 1.9rem; font-weight: 800; line-height: 1.1; margin: .25rem 0 .5rem; }
.auth-logo span { color: var(--naranja); }
.auth-tagline { font-size: .98rem; opacity: .85; margin-bottom: 1.5rem; }
.auth-valueprops { list-style: none; display: flex; flex-direction: column; gap: .55rem; }
.auth-valueprops li { position: relative; padding-left: 1.4rem; font-size: .95rem; opacity: .92; }
.auth-valueprops li::before {
  content: "\25B8"; /* ▸ */
  position: absolute;
  left: 0;
  color: var(--naranja);
  font-weight: 700;
}

/* ── Lado del formulario (derecha) ── */
.auth-form-side {
  flex: 1 1 56%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2.5rem 1.5rem;
  background: var(--bg);
}
.auth-messages { width: 100%; max-width: 400px; margin-bottom: 1rem; }

.auth-card {
  width: 100%;
  max-width: 400px;
  background: var(--surface);
  border-radius: 16px;
  box-shadow: 0 14px 40px rgba(26, 39, 68, .16);
  padding: 2.25rem 2rem;
}
.auth-title { font-size: 1.5rem; font-weight: 800; color: var(--heading); text-align: center; }
.auth-sub { font-size: .9rem; color: var(--text-muted); text-align: center; margin: .25rem 0 1.5rem; }

/* ── Caja de cuenta demo ── */
.auth-demo {
  margin-top: 1.4rem;
  border: 1.5px dashed var(--naranja);
  background: var(--naranja-suave);
  border-radius: 10px;
  padding: .85rem 1rem;
}
.auth-demo-title {
  font-size: .68rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: .6px;
  color: #b5610a;
  margin-bottom: .25rem;
}
.auth-demo-creds { font-size: .85rem; color: var(--text); }
.auth-demo-fill {
  margin-top: .6rem;
  background: var(--naranja);
  color: #fff;
  border: none;
  border-radius: 7px;
  padding: .4rem .85rem;
  font-family: 'Nunito', sans-serif;
  font-weight: 800;
  font-size: .8rem;
  cursor: pointer;
  transition: var(--transicion);
}
.auth-demo-fill:hover { background: #e07d18; }

.auth-foot { text-align: center; font-size: .88rem; color: var(--text-muted); margin-top: 1.3rem; }
.auth-foot a { color: var(--azul-claro); font-weight: 700; }
.auth-foot a:hover { color: var(--naranja); }

/* ── Responsive: apilar en móvil ── */
@media (max-width: 820px) {
  .auth-wrap { flex-direction: column; }
  .auth-panel { flex: none; padding: 2rem 1.5rem 1.75rem; text-align: center; }
  .auth-brand { max-width: 100%; }
  .auth-escudo { width: 60px; height: 60px; }
  .auth-valueprops { align-items: center; }
  .auth-code-motif { font-size: 1.6rem; }
  .auth-form-side { padding: 1.75rem 1.25rem 2.5rem; }
}
```

- [ ] **Step 2: Commit** (se verifica en vivo en la Task 8)

```bash
git add static/css/auth.css
git commit -m "feat(login): auth.css con layout inmersivo split panel"
```

---

## Task 3: `base_auth.html` (shell + panel de marca)

**Files:**
- Create: `templates/base_auth.html`

- [ ] **Step 1: Crear el shell**

```html
{% load static %}
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block titulo %}Acceso{% endblock %} | LogicWeb UTA</title>
  <link rel="stylesheet" href="{% static 'css/style.css' %}">
  <link rel="stylesheet" href="{% static 'css/auth.css' %}">
  {% block head_extra %}{% endblock %}
</head>
<body>
  <div class="auth-wrap">

    <!-- ── Panel de marca (izquierda) ── -->
    <aside class="auth-panel">
      <div class="auth-code-motif" aria-hidden="true">{ } &lt;/&gt; ( ) =&gt; [ ] ; // const for if</div>
      <div class="auth-brand">
        <img src="{% static 'img/uta-escudo.svg' %}" alt="Escudo UTA" class="auth-escudo">
        <p class="auth-overline">Universidad Técnica de Ambato</p>
        <h1 class="auth-logo">Logic<span>Web</span> UTA</h1>
        <p class="auth-tagline">Aprendé lógica programando soluciones reales.</p>
        <ul class="auth-valueprops">
          <li>C++ &middot; Python &middot; Java</li>
          <li>Práctica interactiva con pistas</li>
          <li>Seguí tu progreso por unidad</li>
        </ul>
      </div>
    </aside>

    <!-- ── Lado del formulario (derecha) ── -->
    <main class="auth-form-side">
      {% if messages %}
        <div class="auth-messages">
          {% for message in messages %}
            <div class="alert alert-{{ message.tags }}">{{ message }}</div>
          {% endfor %}
        </div>
      {% endif %}
      {% block auth_content %}{% endblock %}
    </main>

  </div>
  {% block auth_scripts %}{% endblock %}
</body>
</html>
```

- [ ] **Step 2: Verificar que Django parsea las plantillas**

Run (desde el worktree): `python manage.py check`
Expected: `System check identified no issues (0 silenced).`

- [ ] **Step 3: Commit**

```bash
git add templates/base_auth.html
git commit -m "feat(login): base_auth.html shell standalone con panel de marca"
```

---

## Task 4: Reescribir `login.html`

**Files:**
- Modify (reescribir completo): `templates/usuarios/login.html`

- [ ] **Step 1: Reemplazar el contenido**

```html
{% extends 'base_auth.html' %}
{% block titulo %}Iniciar Sesión{% endblock %}

{% block auth_content %}
<div class="auth-card">
  <h2 class="auth-title">Iniciar Sesión</h2>
  <p class="auth-sub">Ingresá con tu cuenta para continuar.</p>

  <form method="post">
    {% csrf_token %}
    {% if form.errors %}
      <div class="alert alert-error">Usuario o contraseña incorrectos.</div>
    {% endif %}
    {% for field in form %}
      <div class="form-group">
        <label for="{{ field.id_for_label }}">{{ field.label }}</label>
        {{ field }}
      </div>
    {% endfor %}
    <button type="submit" class="btn btn-primary btn-full mt-2">Ingresar al sistema</button>
  </form>

  <div class="auth-demo">
    <p class="auth-demo-title">Cuenta de demostración</p>
    <p class="auth-demo-creds">Usuario: <strong>demo</strong> &middot; Contraseña: <strong>Demo123*</strong></p>
    <button type="button" class="auth-demo-fill" id="demo-fill">Usar credenciales demo &rarr;</button>
  </div>

  <p class="auth-foot">¿No tienes cuenta? <a href="{% url 'registro' %}">Regístrate aquí</a></p>
</div>
{% endblock %}

{% block auth_scripts %}
<script>
  document.getElementById('demo-fill').addEventListener('click', function () {
    var u = document.getElementById('id_username');
    var p = document.getElementById('id_password');
    if (u) { u.value = 'demo'; u.focus(); }
    if (p) { p.value = 'Demo123*'; }
  });
</script>
{% endblock %}
```

- [ ] **Step 2: `manage.py check`**

Run: `python manage.py check`
Expected: `System check identified no issues`

- [ ] **Step 3: Commit**

```bash
git add templates/usuarios/login.html
git commit -m "feat(login): login institucional inmersivo + caja demo con autofill"
```

---

## Task 5: Reescribir `registro.html`

**Files:**
- Modify (reescribir completo): `templates/usuarios/registro.html`

- [ ] **Step 1: Reemplazar el contenido**

```html
{% extends 'base_auth.html' %}
{% block titulo %}Crear mi cuenta{% endblock %}

{% block auth_content %}
<div class="auth-card">
  <h2 class="auth-title">Crear mi cuenta</h2>
  <p class="auth-sub">Registrate para empezar a practicar.</p>

  <form method="post">
    {% csrf_token %}
    {% for field in form %}
      <div class="form-group">
        <label for="{{ field.id_for_label }}">{{ field.label }}</label>
        {{ field }}
        {% if field.errors %}
          <ul class="errorlist">
            {% for error in field.errors %}<li>{{ error }}</li>{% endfor %}
          </ul>
        {% endif %}
      </div>
    {% endfor %}
    <button type="submit" class="btn btn-naranja btn-full mt-2">Crear mi cuenta</button>
  </form>

  <p class="auth-foot">¿Ya tienes cuenta? <a href="{% url 'login' %}">Inicia sesión</a></p>
</div>
{% endblock %}
```

- [ ] **Step 2: `manage.py check`**

Run: `python manage.py check`
Expected: `System check identified no issues`

- [ ] **Step 3: Commit**

```bash
git add templates/usuarios/registro.html
git commit -m "feat(login): registro hereda el shell institucional base_auth"
```

---

## Task 6: Management command `crear_demo` (TDD)

**Files:**
- Create: `apps/ejercicios/management/__init__.py` (vacío)
- Create: `apps/ejercicios/management/commands/__init__.py` (vacío)
- Create: `apps/ejercicios/management/commands/crear_demo.py`
- Test: `apps/ejercicios/tests.py` (está vacío — se reescribe)

- [ ] **Step 1: Escribir el test que falla**

`apps/ejercicios/tests.py`:

```python
from django.test import TestCase
from django.core.management import call_command

from apps.ejercicios.models import Usuario, Tema, Ejercicio, Intento, ProgresoEstudiante


class CrearDemoCommandTest(TestCase):
    def _crear_ejercicio(self):
        tema = Tema.objects.create(nombre_tema='T1', descripcion='x', unidad=1, orden=1)
        return Ejercicio.objects.create(
            titulo='Suma', enunciado='e', categoria='interactivo',
            tema=tema, codigo_cpp='x', solucion_esperada='4', tipo_respuesta='entero',
        )

    def test_crea_usuario_demo_idempotente(self):
        self._crear_ejercicio()
        call_command('crear_demo')
        call_command('crear_demo')  # 2da corrida no debe duplicar

        demos = Usuario.objects.filter(username='demo')
        self.assertEqual(demos.count(), 1)
        demo = demos.first()
        self.assertEqual(demo.rol, 'estudiante')
        self.assertTrue(demo.check_password('Demo123*'))

    def test_siembra_progreso_sin_duplicar(self):
        self._crear_ejercicio()  # 1 ejercicio en la unidad 1
        call_command('crear_demo')
        call_command('crear_demo')

        demo = Usuario.objects.get(username='demo')
        self.assertEqual(Intento.objects.filter(usuario=demo).count(), 1)
        self.assertTrue(
            ProgresoEstudiante.objects.filter(usuario=demo, unidad=1, correctos__gte=1).exists()
        )
```

- [ ] **Step 2: Correr el test y verificar que falla**

Run (desde el worktree): `python manage.py test apps.ejercicios -v 2`
Expected: FALLA con `CommandError: Unknown command: 'crear_demo'`

- [ ] **Step 3: Crear los paquetes de management**

Crear `apps/ejercicios/management/__init__.py` y `apps/ejercicios/management/commands/__init__.py`, ambos **vacíos**.

- [ ] **Step 4: Implementar el command**

`apps/ejercicios/management/commands/crear_demo.py`:

```python
from django.core.management.base import BaseCommand

from apps.ejercicios.models import Usuario, Ejercicio, Intento

DEMO_USERNAME = 'demo'
DEMO_PASSWORD = 'Demo123*'


class Command(BaseCommand):
    help = 'Crea (idempotente) la cuenta demo de estudiante y le siembra algo de progreso.'

    def handle(self, *args, **options):
        usuario, creado = Usuario.objects.get_or_create(
            username=DEMO_USERNAME,
            defaults={
                'first_name': 'Estudiante',
                'last_name': 'Demo',
                'email': 'demo@uta.edu.ec',
                'rol': 'estudiante',
            },
        )
        if creado:
            usuario.set_password(DEMO_PASSWORD)
            usuario.save(update_fields=['password'])
            self.stdout.write(self.style.SUCCESS(f'Cuenta demo creada: {DEMO_USERNAME}'))
        else:
            self.stdout.write(f'Cuenta demo ya existe: {DEMO_USERNAME}')

        # Siembra de progreso: solo si el demo aún no tiene intentos (idempotente).
        if usuario.intentos.exists():
            self.stdout.write('El demo ya tiene intentos; no se siembra de nuevo.')
            return

        ejercicios = list(Ejercicio.objects.filter(activo=True)[:5])
        if not ejercicios:
            self.stdout.write(self.style.WARNING('No hay ejercicios; se omite la siembra de progreso.'))
            return

        for ej in ejercicios:
            Intento.objects.create(
                usuario=usuario,
                ejercicio=ej,
                respuesta_usuario=ej.solucion_esperada or 'demo',
                resultado='correcto',
            )
        self.stdout.write(self.style.SUCCESS(
            f'Sembrados {len(ejercicios)} intentos correctos (el signal actualizó ProgresoEstudiante).'
        ))
```

- [ ] **Step 5: Correr el test y verificar que pasa**

Run: `python manage.py test apps.ejercicios -v 2`
Expected: `Ran 2 tests` ... `OK`

- [ ] **Step 6: Commit**

```bash
git add apps/ejercicios/management apps/ejercicios/tests.py
git commit -m "feat(login): command crear_demo idempotente + tests"
```

---

## Task 7: Wire en `build.sh` + setup de BD local

**Files:**
- Modify: `build.sh`

- [ ] **Step 1: Agregar la línea a `build.sh`**

Después de la línea `python manage.py loaddata fixtures/datos_iniciales.json`, agregar:

```bash

# Crear/actualizar la cuenta demo (idempotente).
python manage.py crear_demo
```

- [ ] **Step 2: Crear la BD local del worktree y sembrar**

Run (desde el worktree, en orden):
```bash
python manage.py migrate
python manage.py loaddata fixtures/datos_iniciales.json
python manage.py crear_demo
```
Expected: migraciones aplicadas, fixtures cargados, y `Cuenta demo creada: demo` + `Sembrados N intentos correctos`.

- [ ] **Step 3: Commit**

```bash
git add build.sh
git commit -m "chore(login): correr crear_demo en el build de Render"
```

---

## Task 8: Verificación en vivo (Playwright)

> Usar **Playwright MCP** (browser real). El preview de Claude puede colgarse; login/registro no tienen highlight.js, pero Playwright es el camino robusto. Guardar screenshots a archivo y leerlos.

**Files:** ninguno (solo verificación).

- [ ] **Step 1: Levantar el server del worktree**

Run en background (desde el worktree): `python manage.py runserver 8011 --noreload`
(Puerto 8011 para no chocar con los otros chats.)

- [ ] **Step 2: Login — render**

- `browser_navigate` → `http://localhost:8011/login/`
- `browser_take_screenshot` → verificar: panel navy a la izquierda (escudo + "Universidad Técnica de Ambato" + "LogicWeb UTA" + 3 value props), card blanca a la derecha con Usuario/Contraseña, caja demo naranja, link "Regístrate aquí".

- [ ] **Step 3: Autofill demo**

- `browser_click` en `#demo-fill`.
- `browser_evaluate`: `document.getElementById('id_username').value + '/' + document.getElementById('id_password').value`
- Expected: `demo/Demo123*`

- [ ] **Step 4: Login real con el demo**

- `browser_click` en el botón "Ingresar al sistema".
- Expected: redirige a `/` (inicio) con sesión iniciada (el navbar muestra "Estudiante Demo" / "Salir").

- [ ] **Step 5: Registro hereda el shell**

- `browser_navigate` → `http://localhost:8011/registro/`
- `browser_take_screenshot` → mismo panel de marca + card con los campos de `RegistroForm`, botón naranja "Crear mi cuenta".

- [ ] **Step 6: Responsive**

- `browser_resize` a 375×800, navegar a `/login/`, screenshot.
- Expected: el split se apila (panel arriba compacto, form abajo), sin scroll horizontal.

- [ ] **Step 7: Estado de error**

- En `/login/`, llenar usuario `noexiste` / pass `malo`, submit.
- Expected: alerta roja "Usuario o contraseña incorrectos." dentro de la card.

- [ ] **Step 8: `manage.py check` final**

Run: `python manage.py check`
Expected: `System check identified no issues`

(No hay commit en esta task salvo que un fix sea necesario; en ese caso, commit del fix.)

---

## Task 9: Cerrar la rama

- [ ] **Step 1: Verificar el árbol**

Run (desde el worktree): `git log --oneline main..HEAD` y `git status`
Expected: ~8 commits de la feature, working tree limpio (salvo `db.sqlite3` gitignored).

- [ ] **Step 2: Coordinación con los otros chats antes del merge**
- Confirmar que el chat de **emojis** NO tocó `templates/usuarios/login.html` ni `registro.html` (acá ya van sin emojis). Si los tocó, este branch los reescribe completos → su cambio se descarta para esos 2 archivos (avisar).
- `build.sh`: si otro chat lo modificó en `main`, resolver el merge manteniendo ambas líneas.

- [ ] **Step 3: Integrar**

Usar la skill **superpowers:finishing-a-development-branch** para elegir merge directo a `main` (fast-forward/`--no-ff`) o PR. Push + (deploy automático de Render al llegar a `main`). Borrar la rama y el worktree al terminar:
```bash
git -C C:/Users/osyanne/proyecto_django worktree remove C:/Users/osyanne/.config/superpowers/worktrees/proyecto_django/login-identidad-uta
```

---

## Self-Review (cobertura del spec)

- ✅ Puerta inmersiva standalone → Task 3 (base_auth) + Task 2 (auth.css).
- ✅ Split panel con value props → Task 2/3.
- ✅ Paleta navy/naranja vía tokens de style.css → Task 2 (vars) + Task 3 (carga style.css).
- ✅ Identidad por escudo + texto → Task 1 + Task 3.
- ✅ Cuenta demo visible + autofill → Task 4.
- ✅ Cuenta demo sembrada idempotente (local + Render) → Task 6 + Task 7.
- ✅ Registro hereda el shell → Task 5.
- ✅ Sin emojis → Tasks 4 y 5 (reescritura limpia).
- ✅ Aislamiento → worktree + archivos nuevos; Task 9 coordina los 2 reescritos + build.sh.
- ✅ Verificación (render, autofill, login, registro, responsive, error) → Task 8.
- ✅ `views/forms/urls` sin cambios → confirmado en File Structure.

Sin placeholders; nombres consistentes (`#demo-fill`, `id_username`, `id_password`, `crear_demo`, `auth-*`).
```
