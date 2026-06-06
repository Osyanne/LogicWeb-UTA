from django.urls import path
from . import views

urlpatterns = [
    path('mi-progreso/', views.mi_progreso, name='mi_progreso'),
    path('mi-progreso/exportar/', views.exportar_csv, name='exportar_csv'),
    path('mi-progreso/exportar/pdf/', views.exportar_pdf, name='exportar_pdf'),
    path('mi-progreso/exportar/excel/', views.exportar_excel, name='exportar_excel'),
]
