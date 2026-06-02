from django.views.generic import ListView, DetailView

from apps.ejercicios.models import Tema, Ejercicio


# ══════════════════════════════════════════════════════════════
#  CONTENIDOS — Vistas basadas en clase (§13.2 del documento)
# ══════════════════════════════════════════════════════════════

class ContenidoListView(ListView):
    """Lista todos los temas agrupados por unidad."""
    model = Tema
    template_name = 'contenidos/lista.html'
    context_object_name = 'temas'
    queryset = Tema.objects.all().order_by('unidad', 'orden')


class TemaDetailView(DetailView):
    """Detalle de un tema con sus ejercicios C++ relacionados."""
    model = Tema
    template_name = 'contenidos/detalle.html'
    context_object_name = 'tema'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['ejercicios'] = Ejercicio.objects.filter(
            tema=self.object, activo=True
        ).order_by('orden')
        # Navegación anterior/siguiente entre unidades (ruta de aprendizaje)
        temas = list(Tema.objects.order_by('unidad', 'orden'))
        idx = temas.index(self.object)
        ctx['tema_anterior'] = temas[idx - 1] if idx > 0 else None
        ctx['tema_siguiente'] = temas[idx + 1] if idx + 1 < len(temas) else None
        return ctx
