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
