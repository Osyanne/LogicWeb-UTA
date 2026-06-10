from django.views.generic import DetailView, ListView

from .models import Guia


class GuiaListView(ListView):
    model = Guia
    template_name = 'guias/lista.html'
    context_object_name = 'guias'
    queryset = Guia.objects.filter(publicada=True)


class GuiaDetailView(DetailView):
    model = Guia
    template_name = 'guias/detalle.html'
    context_object_name = 'guia'

    def get_queryset(self):
        # Solo guías publicadas → 404 para borradores.
        return Guia.objects.filter(publicada=True)
