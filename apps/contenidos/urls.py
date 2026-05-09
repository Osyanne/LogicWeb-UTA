from django.urls import path
from .views import ContenidoListView, TemaDetailView

urlpatterns = [
    path('teoria/', ContenidoListView.as_view(), name='contenidos_lista'),
    path('teoria/<int:pk>/', TemaDetailView.as_view(), name='contenido_detalle'),
]
