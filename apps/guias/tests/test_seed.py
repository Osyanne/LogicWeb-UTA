from django.test import TestCase

from apps.guias.models import Guia


class SeedAPE04Test(TestCase):
    """La data migration 0002 siembra la APE-04 (corre en la BD de test)."""
    def test_ape04_sembrada(self):
        g = Guia.objects.get(slug='ape-04-clases-objetos-metodos')
        self.assertEqual(g.codigo, 'SW-AyLP-APE-04')
        self.assertEqual(g.pdf, 'guias/ape-04.pdf')
        self.assertTrue(g.publicada)
        self.assertIn('Estudiante', g.contenido)

    def test_ape04_es_companion(self):
        """La guía no es solo el enunciado: es un acompañante de estudio + desarrollo."""
        g = Guia.objects.get(slug='ape-04-clases-objetos-metodos')
        for seccion in ['Qué vas a practicar', 'Cómo desarrollarla',
                        'Errores comunes', 'Checklist']:
            self.assertIn(seccion, g.contenido)
