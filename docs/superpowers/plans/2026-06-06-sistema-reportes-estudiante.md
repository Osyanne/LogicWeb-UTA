# Sistema de reportes del estudiante — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enriquecer la página "Mi Progreso" del estudiante con gráficos Chart.js y exportación a PDF y Excel, sobre una capa de servicios reutilizable.

**Architecture:** Capa de servicios (`apps/reportes/services.py`) que calcula los datos una sola vez, consumida por la vista HTML (Chart.js) y por los exportadores (`apps/reportes/exporters.py`: PDF con reportlab, Excel con openpyxl). Ninguna agregación se duplica.

**Tech Stack:** Django 6.0.4 (Python 3.13), reportlab, openpyxl, Chart.js (CDN), Django `TestCase`.

**Spec:** `docs/superpowers/specs/2026-06-06-sistema-reportes-design.md`

> **Nota de commits:** el usuario NO quiere `Co-Authored-By: Claude` en los commits. Usar la convención del repo: `feat(reportes): …`, `refactor(reportes): …`, `test(reportes): …`, `chore(reportes): …`.

> **Entorno:** Windows + PowerShell. Trabajar dentro del venv. Si la activación falla por ExecutionPolicy: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` y reintentar. Alternativa robusta: invocar `.\.venv\Scripts\python.exe` directamente en vez de `python`.

---

## Task 1: Setup — rama, venv, dependencias y baseline verde

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: Crear la rama de la feature**

```powershell
git checkout -b feat/reportes-estudiante
```

- [ ] **Step 2: Crear y activar el venv (Python 3.13)**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python --version    # debe mostrar Python 3.13.x
python -m pip install --upgrade pip
```

- [ ] **Step 3: Instalar dependencias actuales + pytest (dev)**

```powershell
pip install -r requirements.txt
pip install pytest        # solo dev — NO se agrega a requirements.txt
```

- [ ] **Step 4: Confirmar baseline verde ANTES de tocar nada**

```powershell
python manage.py migrate
python manage.py test apps
pytest tests/
```
Expected: `python manage.py test apps` → `OK`; `pytest tests/` → todos PASS. Si algo falla aquí, detenerse y reportar (el baseline debe estar verde antes de empezar). Se usa `test apps` (no `test` a secas) para discovery inequívoco de los tests Django, sin tocar la carpeta `tests/` de pytest.

- [ ] **Step 5: Instalar reportlab + openpyxl y pinear versiones exactas**

```powershell
pip install "reportlab>=4.2,<5" "openpyxl>=3.1,<4"
pip freeze | Select-String -Pattern "^reportlab==|^openpyxl=="
```
Copiar las dos líneas exactas que imprime `pip freeze` (p. ej. `reportlab==4.2.5` y `openpyxl==3.1.5`) y agregarlas al final de `requirements.txt`, después de `psycopg2-binary==2.9.10`:

```
reportlab==<versión que reportó pip freeze>
openpyxl==<versión que reportó pip freeze>
```

- [ ] **Step 6: Verificar que el proyecto sigue arrancando**

```powershell
python manage.py check
```
Expected: `System check identified no issues`.

- [ ] **Step 7: Commit**

```powershell
git add requirements.txt
git commit -m "chore(reportes): agregar reportlab y openpyxl para exportacion PDF/Excel"
```

---

## Task 2: `services.py` — `progreso_estudiante` (capa de datos)

**Files:**
- Create: `apps/reportes/services.py`
- Create: `apps/reportes/tests/__init__.py`
- Test: `apps/reportes/tests/test_services.py`

- [ ] **Step 1: Crear el paquete de tests**

Crear `apps/reportes/tests/__init__.py` vacío (archivo sin contenido).

- [ ] **Step 2: Escribir el test que falla**

Crear `apps/reportes/tests/test_services.py`:

```python
from django.test import TestCase

from apps.ejercicios.models import Usuario, Tema, Ejercicio, Intento
from apps.reportes import services


class ProgresoEstudianteServiceTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(username='est', password='clave12345')
        self.tema = Tema.objects.create(
            nombre_tema='Algoritmos', descripcion='x', unidad=1, orden=1,
        )
        self.ej1 = Ejercicio.objects.create(
            titulo='Suma', enunciado='e', categoria='interactivo', tema=self.tema,
            codigo_cpp='int main(){}', solucion_esperada='5', tipo_respuesta='entero',
        )
        self.ej2 = Ejercicio.objects.create(
            titulo='Resta', enunciado='e', categoria='resuelto', tema=self.tema,
            codigo_cpp='', solucion_esperada='2', tipo_respuesta='entero',
        )

    def test_sin_intentos(self):
        data = services.progreso_estudiante(self.user)
        self.assertEqual(data['total'], 0)
        self.assertEqual(data['correctos'], 0)
        self.assertEqual(data['incorrectos'], 0)
        self.assertEqual(data['porcentaje'], 0)
        self.assertEqual(data['codigos_vistos'], 0)
        self.assertEqual(data['progreso_unidades'], [])
        self.assertEqual(data['intentos'], [])

    def test_cuenta_y_porcentaje(self):
        Intento.objects.create(usuario=self.user, ejercicio=self.ej1, respuesta_usuario='5', resultado='correcto')
        Intento.objects.create(usuario=self.user, ejercicio=self.ej1, respuesta_usuario='9', resultado='incorrecto')
        Intento.objects.create(usuario=self.user, ejercicio=self.ej2, respuesta_usuario='2', resultado='correcto')

        data = services.progreso_estudiante(self.user)
        self.assertEqual(data['total'], 3)
        self.assertEqual(data['correctos'], 2)
        self.assertEqual(data['incorrectos'], 1)
        self.assertEqual(data['porcentaje'], 67)          # round(2/3*100)
        self.assertEqual(data['codigos_vistos'], 1)        # solo ej1 tiene codigo_cpp no vacío

    def test_progreso_unidades_e_intentos(self):
        Intento.objects.create(usuario=self.user, ejercicio=self.ej1, respuesta_usuario='5', resultado='correcto')

        data = services.progreso_estudiante(self.user)
        # el signal post_save creó ProgresoEstudiante para la unidad 1
        self.assertEqual(len(data['progreso_unidades']), 1)
        u = data['progreso_unidades'][0]
        self.assertEqual(u['unidad'], 1)
        self.assertEqual(u['total'], 1)
        self.assertEqual(u['correctos'], 1)
        self.assertEqual(u['porcentaje'], 100)
        self.assertEqual(u['nombre'], dict(Tema.UNIDADES)[1])

        self.assertEqual(len(data['intentos']), 1)
        it = data['intentos'][0]
        self.assertEqual(it['titulo'], 'Suma')
        self.assertEqual(it['unidad'], 1)
        self.assertEqual(it['tema'], 'Algoritmos')
        self.assertEqual(it['categoria'], 'interactivo')
        self.assertEqual(it['categoria_display'], 'Ejercicio Interactivo')
        self.assertTrue(it['codigo_visto'])
        self.assertEqual(it['resultado'], 'correcto')
```

- [ ] **Step 3: Correr el test para verlo fallar**

```powershell
python manage.py test apps.reportes.tests.test_services -v 2
```
Expected: FAIL — `ModuleNotFoundError: No module named 'apps.reportes.services'` (o `AttributeError`).

- [ ] **Step 4: Implementar `services.py`**

Crear `apps/reportes/services.py`:

```python
"""Capa de datos de reportes. Fuente única de verdad: la tabla Intento.

Estas funciones son puras (no tocan HTTP) y devuelven estructuras serializables
consumidas por la vista HTML y por los exportadores (PDF/Excel).
"""
from apps.ejercicios.models import Intento, ProgresoEstudiante, Tema


def progreso_estudiante(user) -> dict:
    intentos_qs = (
        Intento.objects
        .filter(usuario=user)
        .select_related('ejercicio__tema')
    )

    total = intentos_qs.count()
    correctos = intentos_qs.filter(resultado='correcto').count()
    incorrectos = total - correctos
    porcentaje = round((correctos / total * 100) if total > 0 else 0)

    codigos_vistos = (
        intentos_qs
        .filter(ejercicio__codigo_cpp__isnull=False)
        .exclude(ejercicio__codigo_cpp='')
        .values('ejercicio')
        .distinct()
        .count()
    )

    nombres_unidad = dict(Tema.UNIDADES)
    progreso_unidades = [
        {
            'unidad': p.unidad,
            'nombre': nombres_unidad.get(p.unidad, f'U{p.unidad}'),
            'total': p.total,
            'correctos': p.correctos,
            'porcentaje': p.porcentaje(),
        }
        for p in ProgresoEstudiante.objects.filter(usuario=user).order_by('unidad')
    ]

    intentos = [
        {
            'titulo': i.ejercicio.titulo,
            'unidad': i.ejercicio.tema.unidad,
            'tema': i.ejercicio.tema.nombre_tema,
            'categoria': i.ejercicio.categoria,
            'categoria_display': i.ejercicio.get_categoria_display(),
            'codigo_visto': bool(i.ejercicio.codigo_cpp),
            'respuesta': i.respuesta_usuario,
            'resultado': i.resultado,
            'fecha': i.fecha,
        }
        for i in intentos_qs
    ]

    return {
        'total': total,
        'correctos': correctos,
        'incorrectos': incorrectos,
        'porcentaje': porcentaje,
        'codigos_vistos': codigos_vistos,
        'progreso_unidades': progreso_unidades,
        'intentos': intentos,
    }
```

- [ ] **Step 5: Correr el test para verlo pasar**

```powershell
python manage.py test apps.reportes.tests.test_services -v 2
```
Expected: `OK` (3 tests).

- [ ] **Step 6: Commit**

```powershell
git add apps/reportes/services.py apps/reportes/tests/__init__.py apps/reportes/tests/test_services.py
git commit -m "feat(reportes): capa services.progreso_estudiante con tests"
```

---

## Task 3: Refactor de la vista y la plantilla para consumir `services`

**Files:**
- Modify: `apps/reportes/views.py`
- Modify: `templates/reportes/mi_progreso.html` (solo el bloque del historial)
- Test: `apps/reportes/tests/test_views.py`

- [ ] **Step 1: Escribir el test (caracteriza el comportamiento actual)**

Crear `apps/reportes/tests/test_views.py`:

```python
from django.test import TestCase
from django.urls import reverse

from apps.ejercicios.models import Usuario, Tema, Ejercicio, Intento


class MiProgresoViewTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(username='est', password='clave12345')

    def test_requiere_login(self):
        resp = self.client.get(reverse('mi_progreso'))
        self.assertEqual(resp.status_code, 302)

    def test_carga_ok(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse('mi_progreso'))
        self.assertEqual(resp.status_code, 200)

    def test_historial_muestra_intento(self):
        tema = Tema.objects.create(nombre_tema='Algoritmos', descripcion='x', unidad=1, orden=1)
        ej = Ejercicio.objects.create(
            titulo='Suma', enunciado='e', categoria='interactivo', tema=tema,
            codigo_cpp='x', solucion_esperada='5', tipo_respuesta='entero',
        )
        Intento.objects.create(usuario=self.user, ejercicio=ej, respuesta_usuario='5', resultado='correcto')
        self.client.force_login(self.user)
        resp = self.client.get(reverse('mi_progreso'))
        self.assertContains(resp, 'Suma')
        self.assertContains(resp, '<svg')   # iconos SVG, no emojis
```

- [ ] **Step 2: Correr el test (debe pasar contra el código actual)**

```powershell
python manage.py test apps.reportes.tests.test_views -v 2
```
Expected: `OK` (caracteriza el comportamiento previo al refactor).

- [ ] **Step 3: Refactorizar `views.py` (`mi_progreso` y `exportar_csv`)**

Reemplazar el contenido de `apps/reportes/views.py` por:

```python
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
import csv

from . import services


@login_required
def mi_progreso(request):
    data = services.progreso_estudiante(request.user)
    return render(request, 'reportes/mi_progreso.html', {
        'total': data['total'],
        'correctos': data['correctos'],
        'incorrectos': data['incorrectos'],
        'porcentaje': data['porcentaje'],
        'codigos_vistos': data['codigos_vistos'],
        'progreso_unidades': data['progreso_unidades'],
        'intentos': data['intentos'][:20],
        'datos_grafico': {
            'unidades': [u['nombre'] for u in data['progreso_unidades']],
            'porcentajes': [u['porcentaje'] for u in data['progreso_unidades']],
            'correctos': data['correctos'],
            'incorrectos': data['incorrectos'],
        },
    })


@login_required
def exportar_csv(request):
    data = services.progreso_estudiante(request.user)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="mi_progreso_logicweb.csv"'

    writer = csv.writer(response)
    writer.writerow(['Ejercicio', 'Unidad', 'Tema', 'Categoría', 'Tu respuesta', 'Resultado', 'Fecha'])
    for i in data['intentos']:
        writer.writerow([
            i['titulo'],
            f"U{i['unidad']}",
            i['tema'],
            i['categoria_display'],
            i['respuesta'],
            i['resultado'],
            i['fecha'].strftime('%d/%m/%Y %H:%M'),
        ])
    return response
```

- [ ] **Step 4: Actualizar el bloque del historial en la plantilla**

En `templates/reportes/mi_progreso.html`, dentro de `<tbody>`, reemplazar las referencias `intento.ejercicio.*` por las claves del dict. Buscar este bloque:

```html
      <tbody>
        {% for intento in intentos %}
        <tr>
          <td><strong>{{ intento.ejercicio.titulo }}</strong></td>
          <td>
            <span class="chip chip-unidad">U{{ intento.ejercicio.tema.unidad }}</span>
            {{ intento.ejercicio.tema.nombre_tema }}
          </td>
          <td>
            {% if intento.ejercicio.categoria == 'resuelto' %}
              <span class="chip chip-resuelto">Resuelto</span>
            {% else %}
              <span class="chip chip-interactivo">Interactivo</span>
            {% endif %}
          </td>
          <td>
            {% if intento.ejercicio.codigo_cpp %}Visto{% else %}—{% endif %}
          </td>
```

y reemplazarlo por:

```html
      <tbody>
        {% for intento in intentos %}
        <tr>
          <td><strong>{{ intento.titulo }}</strong></td>
          <td>
            <span class="chip chip-unidad">U{{ intento.unidad }}</span>
            {{ intento.tema }}
          </td>
          <td>
            {% if intento.categoria == 'resuelto' %}
              <span class="chip chip-resuelto">Resuelto</span>
            {% else %}
              <span class="chip chip-interactivo">Interactivo</span>
            {% endif %}
          </td>
          <td>
            {% if intento.codigo_visto %}Visto{% else %}—{% endif %}
          </td>
```

(El resto del `<tr>` — Resultado y Fecha — ya usa `intento.resultado` e `intento.fecha`, que siguen siendo claves válidas del dict; no se tocan.)

- [ ] **Step 5: Correr los tests de la vista (siguen verdes tras el refactor)**

```powershell
python manage.py test apps.reportes -v 2
```
Expected: `OK` (services + views).

- [ ] **Step 6: Verificar que no hay emojis en la plantilla (regresión)**

```powershell
pytest tests/test_no_emojis.py -v
```
Expected: PASS (incluye `test_no_emoji_progreso`).

- [ ] **Step 7: Commit**

```powershell
git add apps/reportes/views.py templates/reportes/mi_progreso.html apps/reportes/tests/test_views.py
git commit -m "refactor(reportes): mi_progreso y exportar_csv consumen services"
```

---

## Task 4: `exporters.py` — Excel (openpyxl)

**Files:**
- Create: `apps/reportes/exporters.py`
- Test: `apps/reportes/tests/test_exports.py`

- [ ] **Step 1: Escribir el test que falla**

Crear `apps/reportes/tests/test_exports.py`:

```python
from django.test import TestCase

from apps.ejercicios.models import Usuario, Tema, Ejercicio, Intento
from apps.reportes import services, exporters


def _data(user):
    return services.progreso_estudiante(user)


class ExcelExporterTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            username='est', password='clave12345', first_name='Ana', last_name='Pérez',
        )
        tema = Tema.objects.create(nombre_tema='Algoritmos', descripcion='x', unidad=1, orden=1)
        ej = Ejercicio.objects.create(
            titulo='Suma', enunciado='e', categoria='interactivo', tema=tema,
            codigo_cpp='x', solucion_esperada='5', tipo_respuesta='entero',
        )
        Intento.objects.create(usuario=self.user, ejercicio=ej, respuesta_usuario='5', resultado='correcto')

    def test_excel_es_xlsx(self):
        contenido = exporters.reporte_estudiante_excel(_data(self.user), self.user)
        self.assertIsInstance(contenido, bytes)
        self.assertTrue(contenido.startswith(b'PK'))     # magic de zip/xlsx
        self.assertGreater(len(contenido), 1000)

    def test_excel_estudiante_sin_intentos(self):
        vacio = Usuario.objects.create_user(username='vacio', password='clave12345')
        contenido = exporters.reporte_estudiante_excel(_data(vacio), vacio)
        self.assertTrue(contenido.startswith(b'PK'))
```

- [ ] **Step 2: Correr el test para verlo fallar**

```powershell
python manage.py test apps.reportes.tests.test_exports -v 2
```
Expected: FAIL — `cannot import name 'exporters'` o `AttributeError`.

- [ ] **Step 3: Crear `exporters.py` con la función de Excel**

Crear `apps/reportes/exporters.py`:

```python
"""Exportadores del reporte de progreso del estudiante a Excel y PDF.

Reciben el dict de services.progreso_estudiante(user) y el user, y devuelven bytes.
No tocan HTTP: la vista envuelve los bytes en HttpResponse.
"""
import io

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter


def _nombre(user):
    return user.get_full_name() or user.username


def _estilo_encabezado(ws, fila, ncols):
    relleno = PatternFill('solid', fgColor='4A90E2')
    for col in range(1, ncols + 1):
        c = ws.cell(row=fila, column=col)
        c.font = Font(bold=True, color='FFFFFF')
        c.fill = relleno
        c.alignment = Alignment(horizontal='center')


def _autoancho(ws):
    for col in ws.columns:
        ancho = max((len(str(c.value)) for c in col if c.value is not None), default=10)
        ws.column_dimensions[get_column_letter(col[0].column)].width = min(ancho + 4, 50)


def reporte_estudiante_excel(data: dict, user) -> bytes:
    wb = Workbook()

    # — Hoja Resumen —
    ws = wb.active
    ws.title = 'Resumen'
    ws.append([f'Reporte de progreso — {_nombre(user)}'])
    ws.cell(row=1, column=1).font = Font(bold=True, size=14, color='1F4E79')

    ws.append([])
    ws.append(['Métrica', 'Valor'])
    _estilo_encabezado(ws, ws.max_row, 2)
    ws.append(['Aciertos', data['correctos']])
    ws.append(['Errores', data['incorrectos']])
    ws.append(['Total de intentos', data['total']])
    ws.append(['Porcentaje de éxito', f"{data['porcentaje']}%"])
    ws.append(['Ejercicios estudiados', data['codigos_vistos']])

    ws.append([])
    fila_cab = ws.max_row + 1
    ws.append(['Unidad', 'Total', 'Correctos', 'Porcentaje'])
    _estilo_encabezado(ws, fila_cab, 4)
    for u in data['progreso_unidades']:
        ws.append([u['nombre'], u['total'], u['correctos'], f"{u['porcentaje']}%"])
    _autoancho(ws)

    # — Hoja Historial —
    hist = wb.create_sheet('Historial')
    hist.append(['Ejercicio', 'Unidad', 'Tema', 'Tipo', 'Tu respuesta', 'Resultado', 'Fecha'])
    _estilo_encabezado(hist, 1, 7)
    for i in data['intentos']:
        hist.append([
            i['titulo'],
            f"U{i['unidad']}",
            i['tema'],
            i['categoria_display'],
            i['respuesta'],
            i['resultado'],
            i['fecha'].strftime('%d/%m/%Y %H:%M'),
        ])
    hist.freeze_panes = 'A2'
    hist.auto_filter.ref = f"A1:G{max(hist.max_row, 1)}"
    _autoancho(hist)

    buffer = io.BytesIO()
    wb.save(buffer)
    return buffer.getvalue()
```

- [ ] **Step 4: Correr el test para verlo pasar**

```powershell
python manage.py test apps.reportes.tests.test_exports -v 2
```
Expected: `OK` (2 tests).

- [ ] **Step 5: Commit**

```powershell
git add apps/reportes/exporters.py apps/reportes/tests/test_exports.py
git commit -m "feat(reportes): exportador Excel (openpyxl) con tests"
```

---

## Task 5: `exporters.py` — PDF (reportlab)

**Files:**
- Modify: `apps/reportes/exporters.py`
- Test: `apps/reportes/tests/test_exports.py`

- [ ] **Step 1: Agregar el test que falla**

En `apps/reportes/tests/test_exports.py`, agregar al final:

```python
class PdfExporterTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            username='est', password='clave12345', first_name='Ana', last_name='Pérez',
        )
        tema = Tema.objects.create(nombre_tema='Algoritmos', descripcion='x', unidad=1, orden=1)
        ej = Ejercicio.objects.create(
            titulo='Suma', enunciado='e', categoria='interactivo', tema=tema,
            codigo_cpp='x', solucion_esperada='5', tipo_respuesta='entero',
        )
        Intento.objects.create(usuario=self.user, ejercicio=ej, respuesta_usuario='5', resultado='correcto')

    def test_pdf_es_pdf(self):
        contenido = exporters.reporte_estudiante_pdf(_data(self.user), self.user)
        self.assertIsInstance(contenido, bytes)
        self.assertTrue(contenido.startswith(b'%PDF'))
        self.assertGreater(len(contenido), 1000)

    def test_pdf_estudiante_sin_intentos(self):
        vacio = Usuario.objects.create_user(username='vacio', password='clave12345')
        contenido = exporters.reporte_estudiante_pdf(_data(vacio), vacio)
        self.assertTrue(contenido.startswith(b'%PDF'))
```

- [ ] **Step 2: Correr el test para verlo fallar**

```powershell
python manage.py test apps.reportes.tests.test_exports.PdfExporterTest -v 2
```
Expected: FAIL — `AttributeError: module 'apps.reportes.exporters' has no attribute 'reporte_estudiante_pdf'`.

- [ ] **Step 3: Agregar la función PDF a `exporters.py`**

Agregar los imports al inicio de `apps/reportes/exporters.py` (después de `import io`):

```python
from django.utils import timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
```

Agregar la constante de color (después de los imports):

```python
AZUL_UTA = colors.HexColor('#4a90e2')
```

Agregar al final del archivo:

```python
def _estilo_tabla():
    return TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), AZUL_UTA),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#eef3fb')]),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#cccccc')),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ])


def _pie(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica', 8)
    canvas.setFillColor(colors.HexColor('#888888'))
    canvas.drawString(2 * cm, 1.2 * cm, 'LogicWeb UTA — Reporte generado automáticamente')
    canvas.drawRightString(19 * cm, 1.2 * cm, f'Página {doc.page}')
    canvas.restoreState()


def reporte_estudiante_pdf(data: dict, user) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=2 * cm, bottomMargin=2 * cm, leftMargin=2 * cm, rightMargin=2 * cm,
        title='Reporte de progreso — LogicWeb UTA',
    )
    estilos = getSampleStyleSheet()
    estilo_titulo = ParagraphStyle('TituloUTA', parent=estilos['Title'],
                                   fontSize=16, textColor=AZUL_UTA, spaceAfter=4)
    estilo_sub = ParagraphStyle('Sub', parent=estilos['Normal'],
                                fontSize=10, textColor=colors.HexColor('#555555'))
    estilo_h2 = ParagraphStyle('H2UTA', parent=estilos['Heading2'],
                               fontSize=12, textColor=AZUL_UTA, spaceBefore=14, spaceAfter=6)

    el = []
    el.append(Paragraph('UNIVERSIDAD TÉCNICA DE AMBATO', estilo_titulo))
    el.append(Paragraph('LogicWeb UTA — Reporte de progreso', estilo_sub))
    el.append(Paragraph(f'Estudiante: {_nombre(user)}', estilo_sub))
    el.append(Paragraph(f'Generado: {timezone.localtime():%d/%m/%Y %H:%M}', estilo_sub))
    el.append(Spacer(1, 0.4 * cm))

    # KPIs
    el.append(Paragraph('Resumen', estilo_h2))
    kpis = [
        ['Aciertos', 'Errores', 'Total', '% Éxito', 'Estudiados'],
        [str(data['correctos']), str(data['incorrectos']), str(data['total']),
         f"{data['porcentaje']}%", str(data['codigos_vistos'])],
    ]
    t_kpis = Table(kpis, hAlign='LEFT')
    t_kpis.setStyle(_estilo_tabla())
    el.append(t_kpis)

    # Progreso por unidad
    if data['progreso_unidades']:
        el.append(Paragraph('Progreso por unidad', estilo_h2))
        filas = [['Unidad', 'Total', 'Correctos', '%']]
        for u in data['progreso_unidades']:
            filas.append([u['nombre'], str(u['total']), str(u['correctos']), f"{u['porcentaje']}%"])
        t = Table(filas, hAlign='LEFT', colWidths=[9 * cm, 2.5 * cm, 2.5 * cm, 2 * cm])
        t.setStyle(_estilo_tabla())
        el.append(t)

    # Historial
    el.append(Paragraph('Historial de ejercicios', estilo_h2))
    if data['intentos']:
        filas = [['Ejercicio', 'Unidad / Tema', 'Tipo', 'Resultado', 'Fecha']]
        for i in data['intentos']:
            filas.append([
                i['titulo'],
                f"U{i['unidad']} · {i['tema']}",
                i['categoria_display'],
                i['resultado'],
                i['fecha'].strftime('%d/%m/%Y %H:%M'),
            ])
        t = Table(filas, hAlign='LEFT', repeatRows=1,
                  colWidths=[4.5 * cm, 4.5 * cm, 2.8 * cm, 2.4 * cm, 3 * cm])
        t.setStyle(_estilo_tabla())
        el.append(t)
    else:
        el.append(Paragraph('Aún no has practicado ningún ejercicio.', estilo_sub))

    doc.build(el, onFirstPage=_pie, onLaterPages=_pie)
    return buffer.getvalue()
```

- [ ] **Step 4: Correr el test para verlo pasar**

```powershell
python manage.py test apps.reportes.tests.test_exports -v 2
```
Expected: `OK` (4 tests: Excel + PDF).

- [ ] **Step 5: Commit**

```powershell
git add apps/reportes/exporters.py apps/reportes/tests/test_exports.py
git commit -m "feat(reportes): exportador PDF (reportlab) con tests"
```

---

## Task 6: Endpoints de exportación PDF/Excel + rutas

**Files:**
- Modify: `apps/reportes/views.py`
- Modify: `apps/reportes/urls.py`
- Test: `apps/reportes/tests/test_exports.py`

- [ ] **Step 1: Agregar tests de endpoint que fallan**

En `apps/reportes/tests/test_exports.py`, agregar al final:

```python
from django.urls import reverse


class ExportEndpointTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(username='est', password='clave12345')

    def test_pdf_requiere_login(self):
        self.assertEqual(self.client.get(reverse('exportar_pdf')).status_code, 302)

    def test_excel_requiere_login(self):
        self.assertEqual(self.client.get(reverse('exportar_excel')).status_code, 302)

    def test_pdf_descarga(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse('exportar_pdf'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp['Content-Type'], 'application/pdf')
        self.assertIn('attachment', resp['Content-Disposition'])
        self.assertIn('.pdf', resp['Content-Disposition'])
        self.assertTrue(resp.content.startswith(b'%PDF'))

    def test_excel_descarga(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse('exportar_excel'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(
            resp['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        self.assertIn('attachment', resp['Content-Disposition'])
        self.assertTrue(resp.content.startswith(b'PK'))
```

- [ ] **Step 2: Correr el test para verlo fallar**

```powershell
python manage.py test apps.reportes.tests.test_exports.ExportEndpointTest -v 2
```
Expected: FAIL — `NoReverseMatch: Reverse for 'exportar_pdf' not found`.

- [ ] **Step 3: Agregar las vistas `exportar_pdf` y `exportar_excel`**

En `apps/reportes/views.py`, cambiar el import del módulo para incluir `exporters`:

```python
from . import services, exporters
```

Agregar al final de `apps/reportes/views.py`:

```python
@login_required
def exportar_pdf(request):
    data = services.progreso_estudiante(request.user)
    contenido = exporters.reporte_estudiante_pdf(data, request.user)
    resp = HttpResponse(contenido, content_type='application/pdf')
    resp['Content-Disposition'] = 'attachment; filename="mi_progreso_logicweb.pdf"'
    return resp


@login_required
def exportar_excel(request):
    data = services.progreso_estudiante(request.user)
    contenido = exporters.reporte_estudiante_excel(data, request.user)
    resp = HttpResponse(
        contenido,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    resp['Content-Disposition'] = 'attachment; filename="mi_progreso_logicweb.xlsx"'
    return resp
```

- [ ] **Step 4: Agregar las rutas**

Reemplazar el contenido de `apps/reportes/urls.py` por:

```python
from django.urls import path
from . import views

urlpatterns = [
    path('mi-progreso/', views.mi_progreso, name='mi_progreso'),
    path('mi-progreso/exportar/', views.exportar_csv, name='exportar_csv'),
    path('mi-progreso/exportar/pdf/', views.exportar_pdf, name='exportar_pdf'),
    path('mi-progreso/exportar/excel/', views.exportar_excel, name='exportar_excel'),
]
```

- [ ] **Step 5: Correr el test para verlo pasar**

```powershell
python manage.py test apps.reportes.tests.test_exports -v 2
```
Expected: `OK` (8 tests).

- [ ] **Step 6: Commit**

```powershell
git add apps/reportes/views.py apps/reportes/urls.py apps/reportes/tests/test_exports.py
git commit -m "feat(reportes): endpoints de exportacion PDF y Excel"
```

---

## Task 7: Plantilla — gráficos Chart.js + botones de exportación

**Files:**
- Modify: `templates/reportes/mi_progreso.html`
- Create: `static/js/reportes_charts.js`
- Modify: `static/css/reportes.css`
- Test: `apps/reportes/tests/test_views.py`

- [ ] **Step 1: Agregar tests de la vista que fallan**

En `apps/reportes/tests/test_views.py`, agregar al final de la clase `MiProgresoViewTest`:

```python
    def test_muestra_botones_export_y_datos_grafico(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse('mi_progreso'))
        self.assertContains(resp, reverse('exportar_pdf'))
        self.assertContains(resp, reverse('exportar_excel'))
        self.assertContains(resp, 'id="datos-progreso"')        # json_script de Chart.js

    def test_canvas_aparece_con_intentos(self):
        tema = Tema.objects.create(nombre_tema='Algoritmos', descripcion='x', unidad=1, orden=1)
        ej = Ejercicio.objects.create(
            titulo='Suma', enunciado='e', categoria='interactivo', tema=tema,
            codigo_cpp='x', solucion_esperada='5', tipo_respuesta='entero',
        )
        Intento.objects.create(usuario=self.user, ejercicio=ej, respuesta_usuario='5', resultado='correcto')
        self.client.force_login(self.user)
        resp = self.client.get(reverse('mi_progreso'))
        self.assertContains(resp, 'id="grafico-unidades"')
        self.assertContains(resp, 'id="grafico-aciertos"')
        self.assertContains(resp, 'reportes_charts.js')
```

- [ ] **Step 2: Correr el test para verlo fallar**

```powershell
python manage.py test apps.reportes.tests.test_views -v 2
```
Expected: FAIL — `assertContains` no encuentra `id="datos-progreso"` / `id="grafico-unidades"`.

- [ ] **Step 3: Insertar la sección de gráficos + `json_script` en la plantilla**

En `templates/reportes/mi_progreso.html`, buscar esta línea (comentario del bloque de unidades):

```html
  <!-- Progreso por unidad (RF09 — desglose por unidad) -->
```

y reemplazarla por:

```html
  <!-- Gráficos (Chart.js) -->
  {% if total %}
  <div class="reportes-charts">
    <div class="chart-card">
      <h2>Avance por unidad</h2>
      <div class="chart-canvas-wrap"><canvas id="grafico-unidades"></canvas></div>
    </div>
    <div class="chart-card">
      <h2>Aciertos vs. errores</h2>
      <div class="chart-canvas-wrap"><canvas id="grafico-aciertos"></canvas></div>
    </div>
  </div>
  {% endif %}
  {{ datos_grafico|json_script:"datos-progreso" }}

  <!-- Progreso por unidad (RF09 — desglose por unidad) -->
```

- [ ] **Step 4: Reemplazar la botonera de exportación**

En la misma plantilla, buscar:

```html
  <div class="flex-gap mt-3">
    <a href="{% url 'exportar_csv' %}" class="btn btn-outline">Descargar historial CSV</a>
    <a href="{% url 'ejercicios_interactivos' %}" class="btn btn-primary">Seguir practicando</a>
  </div>
```

y reemplazarlo por:

```html
  <div class="flex-gap mt-3">
    <a href="{% url 'exportar_pdf' %}" class="btn btn-primary">Descargar PDF</a>
    <a href="{% url 'exportar_excel' %}" class="btn btn-outline">Descargar Excel</a>
    <a href="{% url 'exportar_csv' %}" class="btn btn-outline">Descargar CSV</a>
    <a href="{% url 'ejercicios_interactivos' %}" class="btn btn-primary">Seguir practicando</a>
  </div>
```

- [ ] **Step 5: Cargar Chart.js + el script de gráficos en el bloque `scripts`**

En la misma plantilla, buscar:

```html
{% block scripts %}
<script>
  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.progress-bar-fill, .unidad-bar-fill').forEach(function (bar) {
```

y reemplazar SOLO las dos primeras líneas (`{% block scripts %}` + el `<script>` que le sigue) por:

```html
{% block scripts %}
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4"></script>
<script src="{% static 'js/reportes_charts.js' %}"></script>
<script>
  document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('.progress-bar-fill, .unidad-bar-fill').forEach(function (bar) {
```

(Se mantiene intacta la animación de barras existente; solo se agregan los dos `<script src=...>` antes de ella.)

- [ ] **Step 6: Crear `static/js/reportes_charts.js`**

```javascript
// Inicializa los gráficos Chart.js de la página "Mi Progreso".
// Lee los datos desde <script type="application/json" id="datos-progreso">.
(function () {
  var nodo = document.getElementById('datos-progreso');
  if (!nodo || typeof Chart === 'undefined') return;

  var datos = JSON.parse(nodo.textContent);
  var oscuro = document.documentElement.dataset.theme === 'dark';
  Chart.defaults.color = oscuro ? '#cbd5e1' : '#374151';
  Chart.defaults.font.family = "'Segoe UI', system-ui, sans-serif";

  var AZUL = '#4a90e2';

  // Barras: % de acierto por unidad
  var elBarras = document.getElementById('grafico-unidades');
  if (elBarras && datos.unidades.length) {
    new Chart(elBarras, {
      type: 'bar',
      data: {
        labels: datos.unidades,
        datasets: [{
          label: '% de acierto',
          data: datos.porcentajes,
          backgroundColor: AZUL,
          borderRadius: 6,
          maxBarThickness: 64,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
          y: { beginAtZero: true, max: 100, ticks: { callback: function (v) { return v + '%'; } } },
        },
      },
    });
  }

  // Dona: aciertos vs. errores
  var elDona = document.getElementById('grafico-aciertos');
  if (elDona && (datos.correctos + datos.incorrectos) > 0) {
    new Chart(elDona, {
      type: 'doughnut',
      data: {
        labels: ['Aciertos', 'Errores'],
        datasets: [{
          data: [datos.correctos, datos.incorrectos],
          backgroundColor: ['#2e9e5b', '#d64545'],
          borderWidth: 2,
          borderColor: oscuro ? '#1e293b' : '#ffffff',
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '62%',
        plugins: { legend: { position: 'bottom' } },
      },
    });
  }
})();
```

- [ ] **Step 7: Agregar estilos de los gráficos a `reportes.css`**

Agregar al final de `static/css/reportes.css`:

```css
/* ── Gráficos (Chart.js) ─────────────────────────────── */
.reportes-charts {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 1rem;
  margin-bottom: 1.5rem;
}
@media (max-width: 720px) {
  .reportes-charts { grid-template-columns: 1fr; }
}
.chart-card {
  background: var(--surface);
  border-radius: var(--radio);
  box-shadow: var(--shadow);
  padding: 1.25rem 1.5rem;
}
.chart-card h2 {
  font-size: 1rem;
  font-weight: 700;
  color: var(--azul);
  margin-bottom: 1rem;
}
.chart-canvas-wrap { position: relative; height: 240px; }
html[data-theme="dark"] .chart-card h2 { color: #7da0d4; }
```

- [ ] **Step 8: Correr los tests de la vista**

```powershell
python manage.py test apps.reportes.tests.test_views -v 2
```
Expected: `OK`.

- [ ] **Step 9: Verificar regresión de emojis (la plantilla cambió)**

```powershell
pytest tests/test_no_emojis.py -v
```
Expected: PASS (`test_no_emoji_progreso` incluido).

- [ ] **Step 10: Commit**

```powershell
git add templates/reportes/mi_progreso.html static/js/reportes_charts.js static/css/reportes.css apps/reportes/tests/test_views.py
git commit -m "feat(reportes): graficos Chart.js y botones PDF/Excel en Mi Progreso"
```

---

## Task 8: Verificación final + cierre

**Files:** (ninguno nuevo — verificación)

- [ ] **Step 1: Suite completa de Django + chequeos de archivos**

```powershell
python manage.py test apps -v 2
pytest tests/
```
Expected: ambos verdes. Confirma que no se rompió ninguna app (ejercicios, etc.).

- [ ] **Step 2: `collectstatic` (verifica que el nuevo JS se recolecta sin error)**

```powershell
python manage.py collectstatic --no-input
```
Expected: termina sin error e incluye `js/reportes_charts.js`.

- [ ] **Step 3: Verificación manual en el navegador**

```powershell
python manage.py runserver
```
Entrar con la cuenta demo (`demo` / `Demo123*`), ir a "Mi Progreso" y comprobar:
- Se ven los dos gráficos (barras por unidad + dona aciertos/errores).
- Los botones "Descargar PDF", "Descargar Excel" y "Descargar CSV" descargan archivos válidos (el PDF abre, el Excel abre con hojas Resumen + Historial).
- Probar también el modo oscuro (toggle del navbar): los gráficos siguen legibles.

Detener el server con Ctrl+C al terminar.

- [ ] **Step 4: Revisión de la rama**

```powershell
git log --oneline main..HEAD
git status
```
Expected: 7 commits (Tasks 1–7), working tree limpio.

- [ ] **Step 5: Decidir integración**

Usar la skill `superpowers:finishing-a-development-branch` para decidir entre merge a `main`, abrir PR, o seguir. (No hacer push ni merge sin confirmación del usuario.)

---

## Notas de implementación

- **DRY:** toda agregación vive en `services.progreso_estudiante`. Vista, CSV, PDF y Excel la consumen; no se recalcula nada.
- **TDD:** cada Task escribe el test primero, lo ve fallar, implementa, lo ve pasar, commitea.
- **Sin emojis:** la plantilla usa includes SVG. Correr `pytest tests/test_no_emojis.py` tras cualquier cambio de plantilla.
- **Render:** `reportlab` y `openpyxl` son Python puro; `build.sh` ya hace `pip install -r requirements.txt`, así que el deploy los toma sin cambios. Chart.js va por CDN.
- **Diferido:** el panel del docente (ver apéndice del spec) no entra aquí; la capa services/exporters queda lista para extenderse.
