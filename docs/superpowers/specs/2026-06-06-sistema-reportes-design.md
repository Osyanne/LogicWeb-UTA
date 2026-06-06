# Diseño — Sistema de reportes del estudiante

- **Fecha:** 2026-06-06
- **Proyecto:** LogicWeb UTA (Django 6, Render)
- **Estado:** Aprobado (diseño) — pendiente plan de implementación
- **Origen:** El ingeniero (docente del curso) pidió que la página tenga "un buen sistema de reportes" exportable a **PDF** y **Excel**.
- **Alcance:** Solo el **estudiante** (el panel del docente queda diferido para más adelante).

---

## 1. Contexto

Hoy la app `apps/reportes/` tiene:

- `mi_progreso` — el estudiante ve su propio progreso (aciertos, errores, %, código visto, barras CSS por unidad U1–U4, últimos 20 intentos).
- `exportar_csv` — descarga un **CSV** crudo de sus intentos.

El modelo de datos (`apps/ejercicios/models.py`):

- `Intento` (usuario, ejercicio, respuesta, resultado, fecha) → **fuente de verdad**.
- `ProgresoEstudiante` (caché por unidad, recalculado por signal en cada `Intento`).
- `Ejercicio` (categoría, dificultad, lenguaje, tema), `Tema` (4 unidades).

**Faltante:** exportación a PDF y Excel (solo hay CSV), y la página puede enriquecerse con gráficos. `requirements.txt` no incluye librerías de PDF/Excel.

## 2. Objetivos

1. Enriquecer la página "Mi Progreso" con **gráficos Chart.js** (barras de avance por unidad + dona aciertos/errores), además de las tarjetas y barras CSS que ya tiene.
2. Agregar exportación del progreso del estudiante a **PDF** y **Excel** (se mantiene el CSV existente).
3. Refactorizar la lógica de datos a una capa de **servicios** reutilizable por pantalla y exportadores (sin duplicar agregaciones).
4. Mantener consistencia con el proyecto: iconos SVG (sin emojis), `TestCase` de Django, despliegue en Render (Python puro, sin libs de sistema).

## 3. No-objetivos (YAGNI)

- **Panel del docente** (ranking, análisis del curso, detalle de otros alumnos): **diferido**, no entra en esta entrega.
- Sin control de acceso nuevo (basta `@login_required`; cada quien ve solo lo suyo).
- Sin gráficos incrustados dentro del PDF (el PDF es tabular).
- Sin filtros por rango de fechas.
- Sin tocar `crear_demo` (la cuenta `demo` ya tiene progreso sembrado suficiente para ver el reporte y exportar).

## 4. Decisiones de diseño

| Decisión | Elección | Motivo |
|----------|----------|--------|
| Audiencia | **Solo estudiante** | Cambio de alcance: el docente se difiere. |
| Gráficos | Chart.js en pantalla, PDF tabular | Enriquece la vista; PDF liviano y seguro en Render. |
| Arquitectura | **Servicios + exportadores** | Lógica de datos separada de presentación → DRY y testeable. |
| PDF | `reportlab` | Python puro, sin dependencias de sistema (Render-safe). |
| Excel | `openpyxl` | Escribe `.xlsx` real, multi-hoja, Python puro. |
| Chart.js | CDN `@4.4` (jsDelivr resuelve último parche) | Evita problemas con `ManifestStaticFilesStorage`; se carga solo en la página de reportes. |

## 5. Arquitectura

Patrón en capas dentro de `apps/reportes/`:

```
services.py    Función pura de agregación del progreso (ÚNICA fuente de verdad de los datos).
exporters.py   Toma los datos de services y produce bytes PDF / XLSX.
views.py       mi_progreso (HTML + Chart.js) y endpoints de exportación. Llama a services/exporters.
urls.py        Rutas del estudiante.
templates/reportes/mi_progreso.html
static/js/reportes_charts.js
tests/         Paquete de tests por capa.
```

Regla clave: **pantalla, PDF y Excel consumen exactamente la misma función de `services.py`.** Ninguna agregación se duplica.

## 6. API de `services.py`

```python
def progreso_estudiante(user) -> dict:
    # {
    #   total, correctos, incorrectos, porcentaje, codigos_vistos,
    #   progreso_unidades: [ {unidad, nombre, total, correctos, porcentaje} ],
    #   intentos: [ {titulo, unidad, tema, categoria, respuesta, resultado, fecha} ],  # TODOS (orden -fecha)
    # }
```

- Implementación con `aggregate`/`annotate` sobre `Intento` (sin N+1).
- `progreso_unidades` se arma desde `ProgresoEstudiante` (caché ya mantenido por signal), enriquecido con el nombre de la unidad (`Tema.UNIDADES`).
- `intentos` retorna la lista **completa** (los exportadores la usan entera; la vista muestra los últimos 20 con `[:20]`).
- Casos borde: estudiante sin intentos → `porcentaje=0`, listas vacías (sin división por cero).

## 7. Rutas (`urls.py`)

| Ruta | Nombre | Acceso | Descripción |
|------|--------|--------|-------------|
| `mi-progreso/` | `mi_progreso` | `@login_required` | Existente + gráficos Chart.js + botones PDF/Excel. |
| `mi-progreso/exportar/` | `exportar_csv` | `@login_required` | CSV (se mantiene). |
| `mi-progreso/exportar/pdf/` | `exportar_pdf` | `@login_required` | PDF del progreso. |
| `mi-progreso/exportar/excel/` | `exportar_excel` | `@login_required` | Excel del progreso. |

## 8. Exportadores (`exporters.py`)

Cada función recibe los datos de `services.progreso_estudiante(user)` y el `user`, y devuelve `bytes`.

### PDF (`reportlab`, Platypus) — `reporte_estudiante_pdf(data, user) -> bytes`

- Encabezado: "UNIVERSIDAD TÉCNICA DE AMBATO — LogicWeb UTA", subtítulo "Reporte de progreso", fecha de generación, "Estudiante: <nombre>".
- Bloque KPIs: aciertos, errores, % de éxito, ejercicios estudiados.
- Tabla "Progreso por unidad" (unidad, total, correctos, %).
- Tabla "Historial de ejercicios" (ejercicio, unidad/tema, tipo, resultado, fecha) — todos los intentos.
- Estilos: cabeceras de tabla con fondo azul UTA (`#4a90e2`), filas zebra, números alineados, paginación al pie.
- Escudo UTA: opcional. Por defecto encabezado tipográfico; si se commitea `static/img/uta-escudo.png` se incrusta con `Image()` (sin dependencias extra; el SVG **no** se renderiza en runtime).

### Excel (`openpyxl`) — `reporte_estudiante_excel(data, user) -> bytes`

- Hoja `Resumen`: KPIs + tabla de progreso por unidad.
- Hoja `Historial`: todos los intentos (mismas columnas que el CSV actual).
- Encabezados en negrita + fondo, `auto_filter`, anchos de columna ajustados, `freeze_panes` en la fila de encabezado.

### Helpers de respuesta (en `views.py`)

- PDF: `HttpResponse(content_type='application/pdf')` + `Content-Disposition: attachment; filename="mi_progreso_logicweb.pdf"`.
- XLSX: `content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'`, filename `mi_progreso_logicweb.xlsx`.

## 9. Vista y plantilla

- `apps/reportes/views.py`: `mi_progreso` se refactoriza para llamar a `services.progreso_estudiante(request.user)` (misma respuesta que hoy + datos para los gráficos). `exportar_csv` se refactoriza para usar `services` (misma salida). Se agregan `exportar_pdf` y `exportar_excel`.
- `templates/reportes/mi_progreso.html`:
  - Mantiene tarjetas KPI, barra global y progreso por unidad actuales.
  - Agrega un `<canvas>` para **barras de avance por unidad** y otro para **dona aciertos/errores**.
  - Datos de los gráficos embebidos como `<script type="application/json" id="datos-progreso">…</script>` (evita inline JS y problemas de escape).
  - Botonera: "Descargar PDF", "Descargar Excel" (y se mantiene "Descargar CSV").
- `static/js/reportes_charts.js` (NUEVO): lee el JSON embebido e inicializa los Chart.js. Se carga junto con el CDN de Chart.js solo en esta página (vía `{% block scripts %}`).

## 10. Dependencias y despliegue

`requirements.txt` += (fijar última estable al instalar; el repo pinea exacto como `Django==6.0.4`):

```
reportlab==4.2.5
openpyxl==3.1.5
```

Python puro → no requieren paquetes de sistema en Render. Chart.js por CDN (`https://cdn.jsdelivr.net/npm/chart.js@4.4`). Sin cambios en `render.yaml` ni en `build.sh`.

## 11. Plan de pruebas (Django `TestCase`)

- **`test_services.py`** (núcleo): crear usuario + ejercicios + intentos controlados y verificar `progreso_estudiante` (total/correctos/incorrectos/porcentaje/codigos_vistos, contenido de `progreso_unidades` e `intentos`). Caso borde: estudiante sin intentos (sin división por cero).
- **`test_exports.py`**: `exportar_pdf` y `exportar_excel` → 200, `Content-Type` correcto, `Content-Disposition: attachment`, cuerpo no vacío; PDF empieza con `%PDF`, XLSX empieza con `PK`. Requieren login (anónimo → 302).
- **`test_views.py`**: `mi_progreso` renderiza KPIs, el JSON de datos para los gráficos, los `<canvas>` y los botones PDF/Excel; usa `<svg` (no emojis). El CSV existente sigue funcionando.
- Regresión: la suite existente (notificaciones, sin-emojis, vistas) sigue verde.

## 12. Riesgos y mitigaciones

- **Cold start en Render (free):** `reportlab`/`openpyxl` son livianos; sin matplotlib. Riesgo bajo.
- **Escape de datos en el JSON de Chart.js:** usar `json_script` de Django o un `<script type="application/json">` con `|escapejs`/serialización segura.
- **Versiones de libs:** pinear exacto tras confirmar la última estable en `pip install`.

## 13. Archivos a crear / modificar

**Crear:**
- `apps/reportes/services.py`
- `apps/reportes/exporters.py`
- `apps/reportes/tests/__init__.py`, `test_services.py`, `test_exports.py`, `test_views.py`
- `static/js/reportes_charts.js`
- (opcional) `static/img/uta-escudo.png`

**Modificar:**
- `apps/reportes/views.py` (refactor a services + `exportar_pdf` + `exportar_excel`)
- `apps/reportes/urls.py` (rutas pdf/excel)
- `templates/reportes/mi_progreso.html` (gráficos + botones)
- `static/css/reportes.css` (estilos de los gráficos/botonera, si hace falta)
- `requirements.txt` (reportlab, openpyxl)

---

## Apéndice — Diferido para una próxima entrega (panel del docente)

Si más adelante se retoma: panel para `rol == 'admin'` con resumen del curso (KPIs), ranking por estudiante, análisis de ejercicios y detalle individual, todo exportable. Requeriría `permissions.py` (`docente_required`), rutas `docente/…`, plantillas nuevas y extender `crear_demo` con un docente + estudiantes sembrados. La capa `services.py`/`exporters.py` de esta entrega está pensada para extenderse a ese caso sin reescribir.
