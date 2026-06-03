from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Tema, Ejercicio, Retroalimentacion, Intento, Notificacion


# ── Usuario ──────────────────────────────────────────────────
@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display  = ('username', 'email', 'get_full_name', 'rol', 'is_active')
    list_filter   = ('rol', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    fieldsets     = UserAdmin.fieldsets + (
        ('Rol LogicWeb', {'fields': ('rol',)}),
    )


# ── Tema ─────────────────────────────────────────────────────
@admin.register(Tema)
class TemaAdmin(admin.ModelAdmin):
    list_display  = ('__str__', 'unidad', 'orden')
    list_filter   = ('unidad',)
    ordering      = ('unidad', 'orden')
    search_fields = ('nombre_tema',)


# ── Retroalimentación inline (se edita dentro del ejercicio) ─
class RetroalimentacionInline(admin.StackedInline):
    model  = Retroalimentacion
    extra  = 1


# ── Ejercicio ────────────────────────────────────────────────
@admin.register(Ejercicio)
class EjercicioAdmin(admin.ModelAdmin):
    list_display  = ('titulo', 'tema', 'categoria', 'dificultad', 'tipo_respuesta', 'activo')
    list_filter   = ('categoria', 'dificultad', 'tema__unidad', 'activo')
    search_fields = ('titulo', 'enunciado')
    ordering      = ('tema__unidad', 'tema__orden', 'orden')
    inlines       = [RetroalimentacionInline]

    fieldsets = (
        ('Información básica', {
            'fields': ('titulo', 'tema', 'categoria', 'dificultad', 'orden', 'activo')
        }),
        ('Enunciado e IPO', {
            'fields': ('enunciado', 'entrada', 'proceso', 'salida', 'pseudocodigo')
        }),
        ('Código C++ educativo', {
            'classes': ('wide',),
            'description': '⚠️ Este código se muestra al estudiante como contenido educativo. NO se ejecuta en el servidor.',
            'fields': ('codigo_cpp',)
        }),
        ('Respuesta esperada (solo ejercicios interactivos)', {
            'fields': ('solucion_esperada', 'tipo_respuesta')
        }),
    )


# ── Intento ──────────────────────────────────────────────────
@admin.register(Intento)
class IntentoAdmin(admin.ModelAdmin):
    list_display  = ('usuario', 'ejercicio', 'resultado', 'fecha')
    list_filter   = ('resultado', 'ejercicio__tema__unidad')
    search_fields = ('usuario__username',)
    readonly_fields = ('usuario', 'ejercicio', 'respuesta_usuario', 'resultado', 'fecha')


# ── Notificacion ─────────────────────────────────────────────
@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display  = ('usuario', 'tipo', 'clave', 'titulo', 'leida', 'fecha')
    list_filter   = ('tipo', 'leida')
    search_fields = ('usuario__username', 'clave', 'titulo')
