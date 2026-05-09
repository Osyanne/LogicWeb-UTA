from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Count, Q


@receiver(post_save, sender='ejercicios.Intento')
def actualizar_progreso_estudiante(sender, instance, created, **kwargs):
    """
    Se dispara cada vez que se guarda un Intento.
    Recalcula y actualiza el caché ProgresoEstudiante del estudiante
    para la unidad correspondiente al ejercicio intentado.
    """
    if not created:
        return

    from .models import ProgresoEstudiante, Intento

    unidad = instance.ejercicio.tema.unidad

    stats = Intento.objects.filter(
        usuario=instance.usuario,
        ejercicio__tema__unidad=unidad,
    ).aggregate(
        total=Count('id'),
        correctos=Count('id', filter=Q(resultado='correcto')),
    )

    ProgresoEstudiante.objects.update_or_create(
        usuario=instance.usuario,
        unidad=unidad,
        defaults={
            'total': stats['total'] or 0,
            'correctos': stats['correctos'] or 0,
        },
    )
