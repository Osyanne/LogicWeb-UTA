from django.db import models
from django.contrib.auth.models import AbstractUser


# ─────────────────────────────────────────
#  USUARIO (extiende AbstractUser de Django)
# ─────────────────────────────────────────
class Usuario(AbstractUser):
    ROL_CHOICES = [('estudiante', 'Estudiante'), ('admin', 'Administrador')]
    rol = models.CharField(max_length=20, choices=ROL_CHOICES, default='estudiante')

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.rol})"


# ─────────────────────────────────────────
#  TEMA  (organiza los ejercicios por unidad)
# ─────────────────────────────────────────
class Tema(models.Model):
    UNIDADES = [
        (1, 'U1: Lógica, Algoritmos y Pseudocódigo'),
        (2, 'U2: Variables, Operadores y Estructuras de Control'),
        (3, 'U3: Programación Orientada a Objetos'),
        (4, 'U4: Estructuras de Datos'),
    ]
    nombre_tema  = models.CharField(max_length=100)
    descripcion  = models.TextField(verbose_name='Teoría resumida')
    unidad       = models.IntegerField(choices=UNIDADES)
    orden        = models.IntegerField(default=0, help_text='Posición dentro de la unidad')

    class Meta:
        ordering = ['unidad', 'orden']
        verbose_name = 'Tema'
        verbose_name_plural = 'Temas'

    def __str__(self):
        return f"U{self.unidad} — {self.nombre_tema}"


# ─────────────────────────────────────────
#  EJERCICIO  (campo codigo_cpp = contenido educativo C++)
# ─────────────────────────────────────────
class Ejercicio(models.Model):
    CATEGORIAS   = [('resuelto', 'Ejercicio Resuelto'), ('interactivo', 'Ejercicio Interactivo')]
    DIFICULTADES = [('basico', 'Básico'), ('medio', 'Medio'), ('avanzado', 'Avanzado')]
    TIPOS_RESP   = [('entero', 'Número entero'), ('decimal', 'Número decimal'), ('texto', 'Texto')]
    LENGUAJES    = [('cpp', 'C++'), ('python', 'Python')]

    titulo             = models.CharField(max_length=200)
    enunciado          = models.TextField()
    categoria          = models.CharField(max_length=20, choices=CATEGORIAS)
    dificultad         = models.CharField(max_length=20, choices=DIFICULTADES, default='basico')
    tema               = models.ForeignKey(Tema, on_delete=models.CASCADE, related_name='ejercicios')
    orden              = models.IntegerField(default=0)
    activo             = models.BooleanField(default=True)

    # ── IPO (Entrada-Proceso-Salida) ──
    entrada            = models.TextField(blank=True, verbose_name='Entradas (IPO)')
    proceso            = models.TextField(blank=True, verbose_name='Proceso (IPO)')
    salida             = models.TextField(blank=True, verbose_name='Salidas (IPO)')
    pseudocodigo       = models.TextField(blank=True, verbose_name='Pseudocódigo')

    lenguaje           = models.CharField(
        max_length=10, choices=LENGUAJES, default='cpp',
        verbose_name='Lenguaje del código',
    )

    # ── Contenido de código educativo (NO se ejecuta — es texto almacenado) ──
    codigo_cpp         = models.TextField(
        verbose_name='Código educativo (C++ o Python)',
        help_text='Código que el estudiante leerá. NO se ejecuta en el servidor.'
    )

    # ── Para ejercicios interactivos ──
    solucion_esperada  = models.TextField(
        verbose_name='Respuesta esperada',
        help_text='Valor correcto. Python lo compara con la respuesta del estudiante.'
    )
    tipo_respuesta     = models.CharField(
        max_length=10, choices=TIPOS_RESP, default='entero',
        help_text='Tipo de dato de la respuesta esperada (para validación inteligente).'
    )

    class Meta:
        ordering = ['tema__unidad', 'tema__orden', 'orden']
        verbose_name = 'Ejercicio'
        verbose_name_plural = 'Ejercicios'

    def __str__(self):
        return f"[{self.get_categoria_display()}] {self.titulo}"

    def evaluar(self, respuesta_usuario: str) -> bool:
        """
        Comparación inteligente para evitar falsos negativos como '120' vs '120.0'.
        - Entero  : int(resp) == int(sol)
        - Decimal : abs(float(resp) - float(sol)) < 0.001
        - Texto   : lowercase + strip
        """
        resp = respuesta_usuario.strip().replace(',', '.')
        sol  = self.solucion_esperada.strip().replace(',', '.')

        if self.tipo_respuesta == 'entero':
            try:
                return int(float(resp)) == int(float(sol))
            except ValueError:
                return False

        elif self.tipo_respuesta == 'decimal':
            try:
                return abs(float(resp) - float(sol)) < 0.001
            except ValueError:
                return False

        else:  # texto
            return resp.lower() == sol.lower()


# ─────────────────────────────────────────
#  RETROALIMENTACION  (mensajes por ejercicio)
# ─────────────────────────────────────────
class Retroalimentacion(models.Model):
    ejercicio        = models.OneToOneField(
        Ejercicio, on_delete=models.CASCADE, related_name='retroalimentacion'
    )
    mensaje_correcto = models.TextField()
    mensaje_error    = models.TextField()
    recomendacion    = models.TextField(blank=True, help_text='Tema o ejercicio recomendado para repasar.')

    class Meta:
        verbose_name = 'Retroalimentación'
        verbose_name_plural = 'Retroalimentaciones'

    def __str__(self):
        return f"Retroalim. → {self.ejercicio.titulo}"


# ─────────────────────────────────────────
#  INTENTO  (historial del estudiante)
# ─────────────────────────────────────────
class Intento(models.Model):
    RESULTADOS = [('correcto', 'Correcto'), ('incorrecto', 'Incorrecto')]

    usuario          = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='intentos')
    ejercicio        = models.ForeignKey(Ejercicio, on_delete=models.CASCADE, related_name='intentos')
    respuesta_usuario = models.TextField()
    resultado        = models.CharField(max_length=20, choices=RESULTADOS)
    fecha            = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Intento'
        verbose_name_plural = 'Intentos'

    def __str__(self):
        return f"{self.usuario.username} → {self.ejercicio.titulo} ({self.resultado})"


# ─────────────────────────────────────────
#  PROGRESO ESTUDIANTE  (caché por unidad — actualizado por signal)
# ─────────────────────────────────────────
class ProgresoEstudiante(models.Model):
    usuario    = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='progreso_unidades')
    unidad     = models.IntegerField()
    total      = models.IntegerField(default=0)
    correctos  = models.IntegerField(default=0)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('usuario', 'unidad')
        ordering = ['unidad']
        verbose_name = 'Progreso por unidad'
        verbose_name_plural = 'Progresos por unidad'

    def porcentaje(self):
        return round((self.correctos / self.total * 100) if self.total > 0 else 0)

    def __str__(self):
        return f"{self.usuario.username} — U{self.unidad}: {self.correctos}/{self.total}"
