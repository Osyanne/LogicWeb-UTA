# Notificaciones de logros — Plan de implementación

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dar al estudiante un feed de notificaciones de logros (campanita 🔔 + página `/notificaciones/`) generadas automáticamente cuando alcanza hitos de práctica.

**Architecture:** Modelo `Notificacion` persistente con `clave` única por usuario (dedup). Un receiver `post_save` de `Intento` (hermano del que ya recalcula el progreso) llama a `otorgar_logros(usuario)`, que evalúa 3 familias de logros y crea las notificaciones que falten vía `get_or_create` (idempotente). Un context processor inyecta el conteo de no-leídas + las últimas 5 al navbar global. Cero cambios en las vistas de respuesta.

**Tech Stack:** Django 6.0.4, SQLite (local) / PostgreSQL (Render), test runner nativo de Django (`manage.py test`, sin pytest), JS vanilla, CSS con variables semánticas (claro/oscuro).

---

## Notas de ejecución (LEER ANTES DE EMPEZAR)

- **Working directory:** todos los comandos `manage.py` se corren **desde `C:\Users\osyanne\proyecto_django`**. Hay un `manage.py` huérfano en el home (`C:\Users\osyanne\`) que apunta a `logicweb.settings` (inexistente) y secuestra el comando si se corre desde ahí → `ModuleNotFoundError: No module named 'logicweb'`. El proyecto usa el paquete `config`.
- **Python:** el de la Microsoft Store (`python` resuelve bien desde `proyecto_django`). Sin venv.
- **Tests:** runner nativo. Comando base: `python manage.py test apps.ejercicios -v 2`. Para un módulo: `python manage.py test apps.ejercicios.tests.test_logros -v 2`.
- **Commits:** uno por tarea (o por ciclo rojo→verde). **Sin `Co-Authored-By`.** Estilo conventional commits en español, como el resto del repo.
- **Alcance de logros (decisión):** volumen y primeros pasos cuentan **solo ejercicios `interactivo`** (no los `resuelto`, que también generan un `Intento` correcto al verse). "Completar unidad" ya usa solo interactivos. Esto hace los logros honestos (premian práctica).
- **Decisión de tests:** para aislar `otorgar_logros()` del signal, los tests de `test_logros.py` crean intentos con `Intento.objects.bulk_create([...])` (NO dispara `post_save`) y luego llaman a la función manualmente. El test del signal (`test_signals.py`) usa `Intento.objects.create()` (sí dispara) y verifica el otorgamiento automático.

## File Structure

**Nuevos:**
- `apps/ejercicios/logros.py` — lógica de otorgamiento (sin tocar BD salvo `get_or_create`).
- `apps/ejercicios/context_processors.py` — inyecta datos de notificaciones al navbar.
- `apps/ejercicios/migrations/0006_notificacion.py` — generada por `makemigrations`.
- `apps/ejercicios/tests/__init__.py` + `test_logros.py` + `test_signals.py` + `test_vistas.py`.
- `templates/notificaciones/lista.html` — página del feed completo.
- `static/css/notificaciones.css` — estilos campanita + dropdown + feed.
- `static/js/notificaciones.js` — toggle del dropdown.

**Modificados:**
- `apps/ejercicios/models.py` — modelo `Notificacion`.
- `apps/ejercicios/admin.py` — registrar `Notificacion`.
- `apps/ejercicios/signals.py` — receiver `generar_notificaciones_logros`.
- `apps/ejercicios/views.py` — view `notificaciones`.
- `apps/ejercicios/urls.py` — ruta `notificaciones/`.
- `templates/base.html` — campanita + `<script>`.
- `config/settings.py` — registrar el context processor.

---

## Task 1: Modelo `Notificacion` + migración + admin

**Files:**
- Modify: `apps/ejercicios/models.py` (añadir al final)
- Modify: `apps/ejercicios/admin.py`
- Create: `apps/ejercicios/migrations/0006_notificacion.py` (vía makemigrations)

- [ ] **Step 1: Añadir el modelo al final de `apps/ejercicios/models.py`**

```python
# ─────────────────────────────────────────
#  NOTIFICACION  (feed de logros del estudiante)
# ─────────────────────────────────────────
class Notificacion(models.Model):
    TIPOS = [
        ('unidad',      'Unidad completada'),
        ('primer_paso', 'Primer paso'),
        ('volumen',     'Volumen'),
    ]
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='notificaciones')
    tipo    = models.CharField(max_length=20, choices=TIPOS)
    clave   = models.CharField(max_length=50, help_text='Identificador único del logro por usuario.')
    titulo  = models.CharField(max_length=150)
    mensaje = models.TextField()
    icono   = models.CharField(max_length=8, default='🔔')
    leida   = models.BooleanField(default=False)
    fecha   = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'clave')   # cada logro se otorga una sola vez
        ordering = ['-fecha']
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'

    def __str__(self):
        return f"{self.usuario.username} — {self.titulo}"
```

- [ ] **Step 2: Registrar en `apps/ejercicios/admin.py`**

Añadir el import de `Notificacion` a la línea de imports existente y registrar:

```python
from .models import Notificacion

@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo', 'clave', 'titulo', 'leida', 'fecha')
    list_filter = ('tipo', 'leida')
    search_fields = ('usuario__username', 'clave', 'titulo')
```

- [ ] **Step 3: Generar la migración**

Run (desde `C:\Users\osyanne\proyecto_django`):
```
python manage.py makemigrations ejercicios
```
Expected: `Migrations for 'ejercicios': 0006_notificacion.py - Create model Notificacion`

- [ ] **Step 4: Aplicar y verificar**

Run:
```
python manage.py migrate
python manage.py check
```
Expected: migración aplicada sin error; `System check identified no issues`.

- [ ] **Step 5: Commit**

```
git add apps/ejercicios/models.py apps/ejercicios/admin.py apps/ejercicios/migrations/0006_notificacion.py
git commit -m "feat(notificaciones): modelo Notificacion + admin + migracion"
```

---

## Task 2: `logros.py` — scaffold + primeros pasos

**Files:**
- Create: `apps/ejercicios/logros.py`
- Create: `apps/ejercicios/tests/__init__.py`
- Create: `apps/ejercicios/tests/test_logros.py`

- [ ] **Step 1: Crear `apps/ejercicios/tests/__init__.py`** (archivo vacío)

```python
```

- [ ] **Step 2: Escribir el test fallido `apps/ejercicios/tests/test_logros.py`**

```python
from django.test import TestCase

from apps.ejercicios.models import Usuario, Tema, Ejercicio, Intento, Notificacion
from apps.ejercicios.logros import otorgar_logros


def crear_ejercicio(tema, lenguaje='cpp', categoria='interactivo', titulo='Ej'):
    return Ejercicio.objects.create(
        titulo=titulo, enunciado='enunciado', categoria=categoria, tema=tema,
        lenguaje=lenguaje, codigo_cpp='// code', solucion_esperada='1', tipo_respuesta='entero',
    )


class PrimerosPasosTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(username='est', password='clave12345')
        self.tema = Tema.objects.create(nombre_tema='Lógica', descripcion='t', unidad=1)

    def _resolver(self, ejercicio):
        # intento correcto SIN disparar el signal (bulk_create no llama post_save)
        Intento.objects.bulk_create([
            Intento(usuario=self.user, ejercicio=ejercicio, respuesta_usuario='1', resultado='correcto')
        ])

    def test_primer_correcto_se_otorga(self):
        self._resolver(crear_ejercicio(self.tema, lenguaje='cpp'))
        otorgar_logros(self.user)
        self.assertTrue(Notificacion.objects.filter(usuario=self.user, clave='primer_correcto').exists())

    def test_primer_lenguaje_se_otorga(self):
        self._resolver(crear_ejercicio(self.tema, lenguaje='java'))
        otorgar_logros(self.user)
        self.assertTrue(Notificacion.objects.filter(usuario=self.user, clave='primer_java').exists())

    def test_no_duplica(self):
        self._resolver(crear_ejercicio(self.tema, lenguaje='cpp'))
        otorgar_logros(self.user)
        otorgar_logros(self.user)
        self.assertEqual(
            Notificacion.objects.filter(usuario=self.user, clave='primer_correcto').count(), 1)

    def test_ver_resuelto_no_cuenta(self):
        self._resolver(crear_ejercicio(self.tema, categoria='resuelto'))
        otorgar_logros(self.user)
        self.assertFalse(Notificacion.objects.filter(usuario=self.user, clave='primer_correcto').exists())
```

- [ ] **Step 3: Run para ver que falla**

Run: `python manage.py test apps.ejercicios.tests.test_logros -v 2`
Expected: FAIL — `ModuleNotFoundError: No module named 'apps.ejercicios.logros'` (o ImportError de `otorgar_logros`).

- [ ] **Step 4: Crear `apps/ejercicios/logros.py`**

```python
"""
Otorgamiento de logros → notificaciones automáticas.

Llamado desde el signal post_save de Intento (solo en intentos correctos).
Cada logro tiene una `clave` única por usuario; get_or_create garantiza que se
otorga una sola vez (idempotente).

Alcance: los logros premian PRÁCTICA INTERACTIVA. Solo se cuentan intentos en
ejercicios con categoria='interactivo'. (Ver un ejercicio resuelto también crea
un Intento correcto, pero NO debe contar como logro.)
"""
from .models import Ejercicio, Intento, Notificacion, Tema

UMBRALES_VOLUMEN = [10, 25, 50]


def _crear(usuario, tipo, clave, titulo, mensaje, icono):
    Notificacion.objects.get_or_create(
        usuario=usuario, clave=clave,
        defaults={'tipo': tipo, 'titulo': titulo, 'mensaje': mensaje, 'icono': icono},
    )


def otorgar_logros(usuario):
    """Evalúa las 3 familias de logros y crea las notificaciones que falten."""
    correctos_ids = set(
        Intento.objects
        .filter(usuario=usuario, resultado='correcto', ejercicio__categoria='interactivo')
        .values_list('ejercicio_id', flat=True)
    )
    if not correctos_ids:
        return

    _primeros_pasos(usuario, correctos_ids)


def _primeros_pasos(usuario, correctos_ids):
    _crear(usuario, 'primer_paso', 'primer_correcto',
           '¡Tu primer ejercicio correcto!',
           'Resolviste tu primer ejercicio de práctica. ¡Así se empieza!', '🌱')

    nombres = dict(Ejercicio.LENGUAJES)
    langs = set(Ejercicio.objects.filter(id__in=correctos_ids).values_list('lenguaje', flat=True))
    for lang in langs:
        nombre = nombres.get(lang, lang)
        _crear(usuario, 'primer_paso', f'primer_{lang}',
               f'¡Tu primer ejercicio en {nombre}!',
               f'Resolviste tu primer ejercicio de práctica en {nombre}.', '🌱')
```

- [ ] **Step 5: Run para ver que pasa**

Run: `python manage.py test apps.ejercicios.tests.test_logros -v 2`
Expected: PASS (4 tests).

- [ ] **Step 6: Commit**

```
git add apps/ejercicios/logros.py apps/ejercicios/tests/__init__.py apps/ejercicios/tests/test_logros.py
git commit -m "feat(notificaciones): logros de primeros pasos (primer correcto + por lenguaje)"
```

---

## Task 3: `logros.py` — volumen acumulado

**Files:**
- Modify: `apps/ejercicios/logros.py`
- Modify: `apps/ejercicios/tests/test_logros.py`

- [ ] **Step 1: Añadir el test al final de `test_logros.py`**

```python
class VolumenTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(username='est', password='clave12345')
        self.tema = Tema.objects.create(nombre_tema='Lógica', descripcion='t', unidad=1)

    def _resolver_n_distintos(self, n):
        ejercicios = [crear_ejercicio(self.tema, titulo=f'Ej{i}') for i in range(n)]
        Intento.objects.bulk_create([
            Intento(usuario=self.user, ejercicio=ej, respuesta_usuario='1', resultado='correcto')
            for ej in ejercicios
        ])

    def test_volumen_10_se_otorga_con_10(self):
        self._resolver_n_distintos(10)
        otorgar_logros(self.user)
        self.assertTrue(Notificacion.objects.filter(usuario=self.user, clave='volumen_10').exists())

    def test_volumen_10_no_con_9(self):
        self._resolver_n_distintos(9)
        otorgar_logros(self.user)
        self.assertFalse(Notificacion.objects.filter(usuario=self.user, clave='volumen_10').exists())

    def test_volumen_cuenta_distintos_no_reintentos(self):
        ej = crear_ejercicio(self.tema)
        Intento.objects.bulk_create([
            Intento(usuario=self.user, ejercicio=ej, respuesta_usuario='1', resultado='correcto')
            for _ in range(10)
        ])
        otorgar_logros(self.user)
        self.assertFalse(Notificacion.objects.filter(usuario=self.user, clave='volumen_10').exists())
```

- [ ] **Step 2: Run para ver que falla**

Run: `python manage.py test apps.ejercicios.tests.test_logros.VolumenTest -v 2`
Expected: FAIL — `test_volumen_10_se_otorga_con_10` falla (no se crea `volumen_10`).

- [ ] **Step 3: Implementar en `logros.py`**

Añadir la llamada dentro de `otorgar_logros` (después de `_primeros_pasos`):
```python
    _primeros_pasos(usuario, correctos_ids)
    _volumen(usuario, len(correctos_ids))
```

Y la función nueva al final del archivo:
```python
def _volumen(usuario, total_distintos):
    for umbral in UMBRALES_VOLUMEN:
        if total_distintos >= umbral:
            _crear(usuario, 'volumen', f'volumen_{umbral}',
                   f'¡{umbral} ejercicios resueltos!',
                   f'Ya llevas {umbral} ejercicios de práctica resueltos correctamente.', '📈')
```

- [ ] **Step 4: Run para ver que pasa**

Run: `python manage.py test apps.ejercicios.tests.test_logros -v 2`
Expected: PASS (7 tests).

- [ ] **Step 5: Commit**

```
git add apps/ejercicios/logros.py apps/ejercicios/tests/test_logros.py
git commit -m "feat(notificaciones): logros de volumen (10/25/50 ejercicios distintos)"
```

---

## Task 4: `logros.py` — unidades completadas

**Files:**
- Modify: `apps/ejercicios/logros.py`
- Modify: `apps/ejercicios/tests/test_logros.py`

- [ ] **Step 1: Añadir el test al final de `test_logros.py`**

```python
class UnidadesTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(username='est', password='clave12345')
        self.tema = Tema.objects.create(nombre_tema='Lógica', descripcion='t', unidad=1)

    def _resolver(self, ej):
        Intento.objects.bulk_create([
            Intento(usuario=self.user, ejercicio=ej, respuesta_usuario='1', resultado='correcto')
        ])

    def test_unidad_completa_se_otorga(self):
        e1 = crear_ejercicio(self.tema, titulo='A')
        e2 = crear_ejercicio(self.tema, titulo='B')
        self._resolver(e1)
        self._resolver(e2)
        otorgar_logros(self.user)
        self.assertTrue(Notificacion.objects.filter(usuario=self.user, clave='unidad_1').exists())

    def test_unidad_incompleta_no_se_otorga(self):
        e1 = crear_ejercicio(self.tema, titulo='A')
        crear_ejercicio(self.tema, titulo='B')  # existe pero no se resuelve
        self._resolver(e1)
        otorgar_logros(self.user)
        self.assertFalse(Notificacion.objects.filter(usuario=self.user, clave='unidad_1').exists())

    def test_resueltos_no_inflan_el_total(self):
        inter = crear_ejercicio(self.tema, titulo='Inter', categoria='interactivo')
        crear_ejercicio(self.tema, titulo='Resu', categoria='resuelto')  # no cuenta para el total
        self._resolver(inter)
        otorgar_logros(self.user)
        self.assertTrue(Notificacion.objects.filter(usuario=self.user, clave='unidad_1').exists())
```

- [ ] **Step 2: Run para ver que falla**

Run: `python manage.py test apps.ejercicios.tests.test_logros.UnidadesTest -v 2`
Expected: FAIL — `unidad_1` no se crea.

- [ ] **Step 3: Implementar en `logros.py`**

Añadir la llamada dentro de `otorgar_logros` (después de `_volumen`):
```python
    _volumen(usuario, len(correctos_ids))
    _unidades(usuario, correctos_ids)
```

Y la función nueva al final del archivo:
```python
def _unidades(usuario, correctos_ids):
    nombres_unidad = dict(Tema.UNIDADES)
    unidades = set(
        Ejercicio.objects.filter(id__in=correctos_ids).values_list('tema__unidad', flat=True)
    )
    for unidad in unidades:
        interactivos_u = set(
            Ejercicio.objects
            .filter(tema__unidad=unidad, categoria='interactivo', activo=True)
            .values_list('id', flat=True)
        )
        if interactivos_u and interactivos_u.issubset(correctos_ids):
            nombre = nombres_unidad.get(unidad, f'U{unidad}')
            _crear(usuario, 'unidad', f'unidad_{unidad}',
                   f'¡Dominaste la U{unidad}!',
                   f'Completaste todos los ejercicios de práctica de «{nombre}».', '🏆')
```

- [ ] **Step 4: Run toda la suite de logros**

Run: `python manage.py test apps.ejercicios.tests.test_logros -v 2`
Expected: PASS (10 tests).

- [ ] **Step 5: Commit**

```
git add apps/ejercicios/logros.py apps/ejercicios/tests/test_logros.py
git commit -m "feat(notificaciones): logro de unidad completada (todos los interactivos de la unidad)"
```

---

## Task 5: Signal — disparo automático en intento correcto

**Files:**
- Modify: `apps/ejercicios/signals.py` (añadir receiver al final)
- Create: `apps/ejercicios/tests/test_signals.py`

- [ ] **Step 1: Escribir el test fallido `apps/ejercicios/tests/test_signals.py`**

```python
from django.test import TestCase

from apps.ejercicios.models import Usuario, Tema, Ejercicio, Intento, Notificacion


class SignalLogrosTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(username='est', password='clave12345')
        self.tema = Tema.objects.create(nombre_tema='Lógica', descripcion='t', unidad=1)
        self.ej = Ejercicio.objects.create(
            titulo='Suma', enunciado='2+3', categoria='interactivo', tema=self.tema,
            lenguaje='cpp', codigo_cpp='//', solucion_esperada='5', tipo_respuesta='entero',
        )

    def test_intento_correcto_dispara_notificacion(self):
        Intento.objects.create(usuario=self.user, ejercicio=self.ej,
                               respuesta_usuario='5', resultado='correcto')
        self.assertTrue(
            Notificacion.objects.filter(usuario=self.user, clave='primer_correcto').exists())

    def test_intento_incorrecto_no_dispara(self):
        Intento.objects.create(usuario=self.user, ejercicio=self.ej,
                               respuesta_usuario='9', resultado='incorrecto')
        self.assertEqual(Notificacion.objects.filter(usuario=self.user).count(), 0)
```

- [ ] **Step 2: Run para ver que falla**

Run: `python manage.py test apps.ejercicios.tests.test_signals -v 2`
Expected: FAIL — `test_intento_correcto_dispara_notificacion` (no se crea la notificación porque el receiver aún no existe).

- [ ] **Step 3: Añadir el receiver al final de `apps/ejercicios/signals.py`**

```python
@receiver(post_save, sender='ejercicios.Intento')
def generar_notificaciones_logros(sender, instance, created, **kwargs):
    """Otorga logros (notificaciones) cuando se registra un intento CORRECTO."""
    if not created or instance.resultado != 'correcto':
        return
    from .logros import otorgar_logros
    otorgar_logros(instance.usuario)
```

(El `import` de `post_save`/`receiver` ya está al inicio de `signals.py`. `apps.py → ready()` ya importa `signals`, así que el receiver se registra sin cambios extra.)

- [ ] **Step 4: Run para ver que pasa**

Run: `python manage.py test apps.ejercicios.tests.test_signals -v 2`
Expected: PASS (2 tests).

- [ ] **Step 5: Commit**

```
git add apps/ejercicios/signals.py apps/ejercicios/tests/test_signals.py
git commit -m "feat(notificaciones): signal que otorga logros en cada intento correcto"
```

---

## Task 6: Context processor + registro en settings

**Files:**
- Create: `apps/ejercicios/context_processors.py`
- Modify: `config/settings.py` (lista `context_processors`)
- Create: `apps/ejercicios/tests/test_vistas.py` (clase `ContextProcessorTest`)

- [ ] **Step 1: Escribir el test fallido `apps/ejercicios/tests/test_vistas.py`**

```python
from django.test import TestCase
from django.urls import reverse

from apps.ejercicios.models import Usuario, Notificacion


class ContextProcessorTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(username='est', password='clave12345')

    def test_conteo_no_leidas(self):
        Notificacion.objects.create(usuario=self.user, tipo='volumen', clave='volumen_10',
                                    titulo='x', mensaje='y', icono='📈', leida=False)
        self.client.force_login(self.user)
        resp = self.client.get(reverse('inicio'))
        self.assertEqual(resp.context['noti_no_leidas'], 1)

    def test_anonimo_no_rompe(self):
        resp = self.client.get(reverse('inicio'))
        self.assertEqual(resp.status_code, 200)
```

- [ ] **Step 2: Run para ver que falla**

Run: `python manage.py test apps.ejercicios.tests.test_vistas.ContextProcessorTest -v 2`
Expected: FAIL — `test_conteo_no_leidas` → `KeyError: 'noti_no_leidas'` (el context processor no está registrado).

- [ ] **Step 3: Crear `apps/ejercicios/context_processors.py`**

```python
from .models import Notificacion


def notificaciones(request):
    """Inyecta el conteo de no-leídas + las últimas 5 al navbar (todas las páginas)."""
    if not request.user.is_authenticated:
        return {}
    qs = Notificacion.objects.filter(usuario=request.user)
    return {
        'noti_no_leidas': qs.filter(leida=False).count(),
        'noti_recientes': qs[:5],
    }
```

- [ ] **Step 4: Registrar en `config/settings.py`**

En `TEMPLATES[0]['OPTIONS']['context_processors']`, añadir la línea final:
```python
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.ejercicios.context_processors.notificaciones',
            ],
```

- [ ] **Step 5: Run para ver que pasa**

Run: `python manage.py test apps.ejercicios.tests.test_vistas.ContextProcessorTest -v 2`
Expected: PASS (2 tests).

- [ ] **Step 6: Commit**

```
git add apps/ejercicios/context_processors.py config/settings.py apps/ejercicios/tests/test_vistas.py
git commit -m "feat(notificaciones): context processor con conteo + recientes para el navbar"
```

---

## Task 7: View + URL + template de la página `/notificaciones/`

**Files:**
- Modify: `apps/ejercicios/views.py`
- Modify: `apps/ejercicios/urls.py`
- Create: `templates/notificaciones/lista.html`
- Modify: `apps/ejercicios/tests/test_vistas.py` (clase `NotificacionesVistaTest`)

- [ ] **Step 1: Añadir el test a `test_vistas.py`**

```python
class NotificacionesVistaTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(username='est', password='clave12345')

    def test_requiere_login(self):
        resp = self.client.get(reverse('notificaciones'))
        self.assertEqual(resp.status_code, 302)

    def test_pagina_carga_y_marca_leidas(self):
        Notificacion.objects.create(usuario=self.user, tipo='volumen', clave='volumen_10',
                                    titulo='¡10 ejercicios!', mensaje='y', icono='📈', leida=False)
        self.client.force_login(self.user)
        resp = self.client.get(reverse('notificaciones'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '¡10 ejercicios!')
        self.assertEqual(Notificacion.objects.filter(usuario=self.user, leida=False).count(), 0)
```

- [ ] **Step 2: Run para ver que falla**

Run: `python manage.py test apps.ejercicios.tests.test_vistas.NotificacionesVistaTest -v 2`
Expected: FAIL — `NoReverseMatch: 'notificaciones'` (la ruta no existe).

- [ ] **Step 3: Añadir la view a `apps/ejercicios/views.py`**

```python
@login_required
def notificaciones(request):
    notis = request.user.notificaciones.all()
    request.user.notificaciones.filter(leida=False).update(leida=True)
    return render(request, 'notificaciones/lista.html', {'notificaciones': notis})
```

- [ ] **Step 4: Añadir la ruta a `apps/ejercicios/urls.py`**

Dentro de `urlpatterns`, después de la ruta `comparar/`:
```python
    path('notificaciones/', views.notificaciones, name='notificaciones'),
```

- [ ] **Step 5: Crear `templates/notificaciones/lista.html`**

```html
{% extends 'base.html' %}
{% block titulo %}Notificaciones{% endblock %}

{% block contenido %}
<section class="container noti-page">
  <h1 class="noti-page-title">🔔 Tus notificaciones</h1>

  {% for n in notificaciones %}
    <article class="noti-card">
      <span class="noti-card-ico">{{ n.icono }}</span>
      <div class="noti-card-body">
        <strong class="noti-card-titulo">{{ n.titulo }}</strong>
        <p class="noti-card-msg">{{ n.mensaje }}</p>
        <span class="noti-card-time">hace {{ n.fecha|timesince }}</span>
      </div>
    </article>
  {% empty %}
    <div class="noti-vacio">
      <p>Todavía no tienes notificaciones.</p>
      <p>Resuelve ejercicios de práctica para desbloquear logros. 🌱</p>
    </div>
  {% endfor %}
</section>
{% endblock %}
```

(No hace falta cargar el CSS aquí: la Task 8 añade `notificaciones.css` al `<head>` de `base.html` globalmente, así que esta página lo hereda. Por eso tampoco se necesita `head_extra` ni `{% load static %}` en este template.)

- [ ] **Step 6: Run para ver que pasa**

Run: `python manage.py test apps.ejercicios.tests.test_vistas -v 2`
Expected: PASS (4 tests: 2 context processor + 2 vista).

- [ ] **Step 7: Commit**

```
git add apps/ejercicios/views.py apps/ejercicios/urls.py templates/notificaciones/lista.html apps/ejercicios/tests/test_vistas.py
git commit -m "feat(notificaciones): pagina /notificaciones/ con feed y marcado de leidas"
```

---

## Task 8: Campanita en el navbar + JS + CSS

**Files:**
- Modify: `templates/base.html`
- Create: `static/css/notificaciones.css`
- Create: `static/js/notificaciones.js`

> Esta tarea es de UI; se verifica visualmente en la Task 9. No hay test unitario nuevo (la presencia de la campanita queda cubierta indirectamente y se valida con Playwright).

- [ ] **Step 1: Crear `static/css/notificaciones.css`**

```css
/* ── Campanita en el navbar ── */
.noti-wrap { position: relative; display: inline-flex; align-items: center; }
.noti-btn {
  background: none; border: none; cursor: pointer; font-size: 1.2rem;
  color: #fff; padding: .25rem; position: relative; line-height: 1;
}
.noti-badge {
  position: absolute; top: -4px; right: -6px;
  background: var(--accent, #ff7a18); color: #fff;
  font-size: .68rem; font-weight: 700; line-height: 1;
  padding: .12rem .35rem; border-radius: 999px; min-width: 1.1em; text-align: center;
}

/* ── Dropdown ── */
.noti-dropdown {
  position: absolute; right: 0; top: 130%; width: 320px;
  max-height: 60vh; overflow-y: auto;
  background: var(--surface, #fff); color: var(--text, #222);
  border: 1px solid var(--border, #e0e0e0); border-radius: 12px;
  box-shadow: var(--shadow-hover, 0 8px 24px rgba(0,0,0,.18));
  z-index: 1000; padding: .4rem 0;
}
.noti-dropdown[hidden] { display: none; }
.noti-dropdown-head { font-weight: 700; padding: .5rem 1rem; border-bottom: 1px solid var(--border, #eee); }
.noti-item { display: flex; gap: .6rem; padding: .6rem 1rem; align-items: flex-start; }
.noti-item--nueva { background: rgba(255,122,24,.08); }
.noti-item-ico { font-size: 1.25rem; line-height: 1.2; }
.noti-item-body { display: flex; flex-direction: column; gap: .15rem; }
.noti-item-time { font-size: .72rem; color: var(--text-muted, #888); }
.noti-empty { padding: 1rem; text-align: center; color: var(--text-muted, #888); }
.noti-vertodas {
  display: block; text-align: center; padding: .6rem;
  font-weight: 600; border-top: 1px solid var(--border, #eee); color: var(--accent, #ff7a18);
}

/* ── Página /notificaciones/ ── */
.noti-page { max-width: 760px; margin: 2rem auto; }
.noti-page-title { margin-bottom: 1.2rem; }
.noti-card {
  display: flex; gap: 1rem; padding: 1rem 1.2rem; margin-bottom: .8rem;
  background: var(--surface, #fff); border: 1px solid var(--border, #e0e0e0);
  border-radius: 12px; box-shadow: var(--shadow, 0 2px 8px rgba(0,0,0,.06));
}
.noti-card-ico { font-size: 1.8rem; line-height: 1.1; }
.noti-card-titulo { color: var(--heading, #1f3a5f); }
.noti-card-msg { margin: .2rem 0; color: var(--text, #333); }
.noti-card-time { font-size: .75rem; color: var(--text-muted, #888); }
.noti-vacio { text-align: center; color: var(--text-muted, #888); padding: 3rem 1rem; }
```

> Nota: los nombres de variables (`--surface`, `--text`, `--text-muted`, `--heading`, `--border`, `--shadow`, `--shadow-hover`, `--accent`) son la capa semántica del modo oscuro ya existente. Verificar en `static/css/style.css` (`:root`) que existan; los fallbacks cubren cualquier desajuste. Si alguno no existe, ajustar al nombre real.

- [ ] **Step 2: Crear `static/js/notificaciones.js`**

```javascript
(function () {
  const btn = document.getElementById('noti-toggle');
  const dropdown = document.getElementById('noti-dropdown');
  if (!btn || !dropdown) return;

  function abrir() { dropdown.hidden = false; btn.setAttribute('aria-expanded', 'true'); }
  function cerrar() { dropdown.hidden = true; btn.setAttribute('aria-expanded', 'false'); }

  btn.addEventListener('click', function (e) {
    e.stopPropagation();
    if (dropdown.hidden) { abrir(); } else { cerrar(); }
  });
  document.addEventListener('click', function (e) {
    if (!dropdown.hidden && !dropdown.contains(e.target)) { cerrar(); }
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { cerrar(); }
  });
})();
```

- [ ] **Step 3: Añadir la campanita a `templates/base.html`**

En el `<head>`, junto a los otros `<link>` de CSS (después de `codigo.css`):
```html
  <link rel="stylesheet" href="{% static 'css/notificaciones.css' %}?v=1">
```

En `.navbar-user`, justo después del `</button>` del `#theme-toggle` y dentro del bloque `{% if user.is_authenticated %}` (antes del `👤 {{ user.get_full_name... }}`):
```html
      {% if user.is_authenticated %}
        <div class="noti-wrap">
          <button id="noti-toggle" class="noti-btn" type="button" aria-label="Notificaciones" aria-expanded="false">
            🔔{% if noti_no_leidas %}<span class="noti-badge">{{ noti_no_leidas }}</span>{% endif %}
          </button>
          <div id="noti-dropdown" class="noti-dropdown" hidden>
            <div class="noti-dropdown-head">Notificaciones</div>
            {% for n in noti_recientes %}
              <div class="noti-item {% if not n.leida %}noti-item--nueva{% endif %}">
                <span class="noti-item-ico">{{ n.icono }}</span>
                <div class="noti-item-body">
                  <strong>{{ n.titulo }}</strong>
                  <span class="noti-item-time">hace {{ n.fecha|timesince }}</span>
                </div>
              </div>
            {% empty %}
              <div class="noti-empty">Todavía no tienes notificaciones.</div>
            {% endfor %}
            <a href="{% url 'notificaciones' %}" class="noti-vertodas">Ver todas</a>
          </div>
        </div>
        👤 {{ user.get_full_name|default:user.username }}
```

> Importante: el `{% if user.is_authenticated %}` actual ya envuelve el bloque `👤 ... | Salir`. Insertar la campanita **dentro** de ese mismo `{% if %}`, NO duplicar el `{% if %}`. Revisar el bloque resultante para que abra/cierre una sola vez.

Y junto a los `<script>` del final (después de `main.js`):
```html
  <script src="{% static 'js/notificaciones.js' %}"></script>
```

- [ ] **Step 4: `manage.py check` + suite completa (no debe romper nada)**

Run:
```
python manage.py check
python manage.py test apps.ejercicios -v 2
```
Expected: sin issues; todos los tests PASS (10 logros + 2 signals + 4 vistas = 16).

- [ ] **Step 5: Commit**

```
git add templates/base.html static/css/notificaciones.css static/js/notificaciones.js
git commit -m "feat(notificaciones): campanita en navbar con badge + dropdown (claro/oscuro)"
```

---

## Task 9: Verificación end-to-end (Playwright) + cierre

**Files:** ninguno nuevo (verificación + posibles hotfixes).

> Verificación visual con **Playwright MCP** (no Claude_Preview, que se cuelga con highlight.js — ver memoria del proyecto). Servidor: `python manage.py runserver 8000` desde `proyecto_django`.

- [ ] **Step 1: Sembrar datos de prueba para ver notificaciones reales**

Run un shell de Django (desde `proyecto_django`):
```
python manage.py shell -c "from apps.ejercicios.models import Usuario, Ejercicio, Intento; u=Usuario.objects.filter(is_superuser=False).first() or Usuario.objects.create_user('demo_noti','x'); e=Ejercicio.objects.filter(categoria='interactivo', activo=True).first(); Intento.objects.create(usuario=u, ejercicio=e, respuesta_usuario=e.solucion_esperada, resultado='correcto'); print('Notis:', list(u.notificaciones.values_list('clave', flat=True)))"
```
Expected: imprime al menos `['primer_correcto', 'primer_<lang>']`.

- [ ] **Step 2: Arrancar el server y loguearse con Playwright**

- `python manage.py runserver 8000` (desde `proyecto_django`).
- Playwright: navegar a `http://localhost:8000/login/`, loguear con el usuario sembrado (o un usuario conocido de la BD).

- [ ] **Step 3: Verificar la campanita (claro)**

- Snapshot del navbar: la 🔔 aparece con badge (nº de no-leídas).
- Clic en la campanita → el dropdown se abre con las notificaciones; "Ver todas" visible.
- Clic afuera → el dropdown se cierra.
- Screenshot a archivo → Read para confirmar visualmente.

- [ ] **Step 4: Verificar la página `/notificaciones/`**

- Navegar a `http://localhost:8000/notificaciones/`: feed completo con icono + título + mensaje + "hace X".
- Volver al navbar: el badge bajó a 0 (se marcaron leídas).

- [ ] **Step 5: Verificar modo oscuro**

- Toggle 🌙 → repetir snapshots de campanita, dropdown y página. Confirmar 0 "islas claras" (dropdown y cards usan `--surface`/`--text`, no fondos claros fijos). Ajustar CSS si algo queda claro en oscuro.

- [ ] **Step 6: Responsive (sanity)**

- `browser_resize` a 375px: la campanita no rompe el layout más de lo que el navbar ya desborda (problema preexistente del sub-proyecto responsive). El dropdown (320px) no debe salirse de la pantalla — si lo hace, limitar con `max-width: 92vw` en `.noti-dropdown`.

- [ ] **Step 7: Limpiar datos de prueba (si se creó un usuario demo desechable)**

```
python manage.py shell -c "from apps.ejercicios.models import Usuario; Usuario.objects.filter(username='demo_noti').delete()"
```
(Omitir si se usó un usuario real existente — en ese caso, dejar sus notificaciones.)

- [ ] **Step 8: Commit de hotfixes visuales (si hubo)**

```
git add -A
git commit -m "fix(notificaciones): ajustes visuales tras verificacion (claro/oscuro/responsive)"
```

- [ ] **Step 9: Merge/push a main → Render redeploya**

Seguir el flujo habitual del usuario (él revisa/mergea/pushea). El push a `main` dispara el auto-deploy en Render; `build.sh` corre `collectstatic` + `migrate` (aplica `0006`) automáticamente.

---

## Resumen de verificación final

- [ ] `python manage.py test apps.ejercicios -v 2` → 16 tests PASS.
- [ ] `python manage.py check` → sin issues.
- [ ] Campanita con badge visible (autenticado), dropdown abre/cierra, "Ver todas" funciona.
- [ ] Página `/notificaciones/` lista el feed y marca leídas (badge → 0).
- [ ] Claro y oscuro sin islas claras.
- [ ] Logros reales disparados por un intento correcto (primer_correcto + por lenguaje + volumen/unidad cuando corresponde).
