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
