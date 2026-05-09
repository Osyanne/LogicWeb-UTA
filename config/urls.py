from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.ejercicios.urls')),
    path('', include('apps.contenidos.urls')),
    path('', include('apps.usuarios.urls')),
    path('', include('apps.reportes.urls')),
]
