from django.urls import path

from .views import GuiaDetailView, GuiaListView

urlpatterns = [
    path('guias/', GuiaListView.as_view(), name='guias_lista'),
    path('guias/<slug:slug>/', GuiaDetailView.as_view(), name='guias_detalle'),
]
