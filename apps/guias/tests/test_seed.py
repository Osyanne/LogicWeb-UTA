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
