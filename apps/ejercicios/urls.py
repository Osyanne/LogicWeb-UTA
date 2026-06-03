from django.urls import path
from . import views

urlpatterns = [
    # ── Inicio ──────────────────────────────────────────
    path('', views.inicio, name='inicio'),
    path('comparar/', views.comparar, name='comparar'),
    path('notificaciones/', views.notificaciones, name='notificaciones'),

    # ── Ejercicios resueltos ─────────────────────────────
    path('ejercicios/resueltos/', views.ejercicios_resueltos, name='ejercicios_resueltos'),
    path('ejercicios/resueltos/<int:pk>/', views.ejercicio_resuelto_detalle, name='resuelto_detalle'),

    # ── Ejercicios interactivos ──────────────────────────
    path('ejercicios/practica/', views.ejercicios_interactivos, name='ejercicios_interactivos'),
    path('ejercicios/practica/<int:pk>/', views.ejercicio_interactivo_detalle, name='interactivo_detalle'),
]
