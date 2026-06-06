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
