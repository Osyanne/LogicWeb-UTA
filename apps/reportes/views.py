from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import HttpResponse
import csv

from apps.ejercicios.models import Intento, ProgresoEstudiante, Tema


# ══════════════════════════════════════════════════════════════
#  REPORTES — Progreso del estudiante con desglose por unidad
# ══════════════════════════════════════════════════════════════

@login_required
def mi_progreso(request):
    intentos = Intento.objects.filter(usuario=request.user).select_related('ejercicio__tema')

    total       = intentos.count()
    correctos   = intentos.filter(resultado='correcto').count()
    incorrectos = intentos.filter(resultado='incorrecto').count()
    porcentaje  = round((correctos / total * 100) if total > 0 else 0)

    codigos_vistos = (
        intentos
        .filter(ejercicio__codigo_cpp__isnull=False)
        .exclude(ejercicio__codigo_cpp='')
        .values('ejercicio')
        .distinct()
        .count()
    )

    # ── Progreso por unidad (desde caché de ProgresoEstudiante) ──
    progreso_unidades = ProgresoEstudiante.objects.filter(
        usuario=request.user
    ).order_by('unidad')

    # Enriquecer con el nombre de la unidad
    nombres_unidad = dict(Tema.UNIDADES)
    progreso_con_nombre = [
        {
            'unidad': p.unidad,
            'nombre': nombres_unidad.get(p.unidad, f'U{p.unidad}'),
            'total': p.total,
            'correctos': p.correctos,
            'porcentaje': p.porcentaje(),
        }
        for p in progreso_unidades
    ]

    return render(request, 'reportes/mi_progreso.html', {
        'intentos': intentos[:20],
        'total': total,
        'correctos': correctos,
        'incorrectos': incorrectos,
        'porcentaje': porcentaje,
        'codigos_vistos': codigos_vistos,
        'progreso_unidades': progreso_con_nombre,
    })


@login_required
def exportar_csv(request):
    intentos = Intento.objects.filter(usuario=request.user).select_related('ejercicio__tema')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="mi_progreso_logicweb.csv"'

    writer = csv.writer(response)
    writer.writerow(['Ejercicio', 'Unidad', 'Tema', 'Categoría', 'Tu respuesta', 'Resultado', 'Fecha'])
    for i in intentos:
        writer.writerow([
            i.ejercicio.titulo,
            f"U{i.ejercicio.tema.unidad}",
            i.ejercicio.tema.nombre_tema,
            i.ejercicio.get_categoria_display(),
            i.respuesta_usuario,
            i.resultado,
            i.fecha.strftime('%d/%m/%Y %H:%M'),
        ])
    return response
