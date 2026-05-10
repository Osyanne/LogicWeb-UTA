from django.urls import path
from . import views

urlpatterns = [
    path('mi-progreso/', views.mi_progreso, name='mi_progreso'),
    path('mi-progreso/exportar/', views.exportar_csv, name='exportar_csv'),
]
