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
        .distinct()
    )
    if not correctos_ids:
        return

    _primeros_pasos(usuario, correctos_ids)
    _volumen(usuario, len(correctos_ids))
    _unidades(usuario, correctos_ids)


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


def _volumen(usuario, total_distintos):
    for umbral in UMBRALES_VOLUMEN:
        if total_distintos >= umbral:
            _crear(usuario, 'volumen', f'volumen_{umbral}',
                   f'¡{umbral} ejercicios resueltos!',
                   f'Ya llevas {umbral} ejercicios de práctica resueltos correctamente.', '📈')


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
