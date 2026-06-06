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
