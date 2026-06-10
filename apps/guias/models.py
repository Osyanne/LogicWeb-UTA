from django.db import models


class Guia(models.Model):
    """Guía práctica APE: enunciado en Markdown + PDF oficial + repo GitHub."""
    codigo      = models.CharField('Código APE', max_length=40,
                                   help_text='Ej.: SW-AyLP-APE-04')
    titulo      = models.CharField('Título', max_length=200)
    slug        = models.SlugField('Slug (URL)', unique=True,
                                   help_text='Ej.: ape-04-clases-objetos-metodos')
    resumen     = models.CharField('Resumen', max_length=300, blank=True,
                                   help_text='Una línea para la tarjeta del listado.')
    contenido   = models.TextField('Contenido (Markdown)',
                                   help_text='Enunciado completo en formato Markdown.')
    repo_url    = models.URLField('Repo GitHub', blank=True)
    pdf         = models.CharField('PDF oficial', max_length=200, blank=True,
                                   help_text='Ruta dentro de static/, ej.: guias/ape-04.pdf')
    orden       = models.PositiveIntegerField('Orden', default=0)
    publicada   = models.BooleanField('Publicada', default=True)
    pasos       = models.JSONField('Pasos de desarrollo', default=list, blank=True,
                                   help_text='Lista de pasos (textos) que el estudiante puede marcar.')
    checklist   = models.JSONField('Checklist de entrega', default=list, blank=True,
                                   help_text='Lista de entregables (textos) marcables.')
    quiz        = models.JSONField('Autoevaluación', default=list, blank=True,
                                   help_text='Lista de preguntas: {pregunta, opciones[], correcta, explicacion}.')
    creada      = models.DateTimeField(auto_now_add=True)
    actualizada = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['orden', 'codigo']
        verbose_name = 'Guía APE'
        verbose_name_plural = 'Guías APE'

    def __str__(self):
        return f'{self.codigo} — {self.titulo}'
