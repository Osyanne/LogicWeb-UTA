from django.contrib import admin

from .models import Guia


@admin.register(Guia)
class GuiaAdmin(admin.ModelAdmin):
    list_display  = ('codigo', 'titulo', 'orden', 'publicada')
    list_editable = ('orden', 'publicada')
    list_filter   = ('publicada',)
    search_fields = ('codigo', 'titulo')
    prepopulated_fields = {'slug': ('titulo',)}
    fieldsets = (
        (None, {'fields': ('codigo', 'titulo', 'slug', 'resumen', 'orden', 'publicada')}),
        ('Contenido', {
            'description': 'El contenido se escribe en Markdown (títulos ##, listas, '
                           'bloques de código con triple backtick + lenguaje).',
            'fields': ('contenido',),
        }),
        ('Recursos', {'fields': ('repo_url', 'pdf')}),
    )
