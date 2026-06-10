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
        """Acompañante: prosa en el contenido + widgets interactivos en campos."""
        g = Guia.objects.get(slug='ape-04-clases-objetos-metodos')
        for seccion in ['Qué vas a practicar', 'Errores comunes', 'Recursos']:
            self.assertIn(seccion, g.contenido)
        self.assertTrue(g.pasos)
        self.assertTrue(g.checklist)

    def test_ape04_interactiva(self):
        """Los pasos, el checklist y la autoevaluación están poblados."""
        g = Guia.objects.get(slug='ape-04-clases-objetos-metodos')
        self.assertEqual(len(g.pasos), 8)
        self.assertEqual(len(g.checklist), 6)
        self.assertEqual(len(g.quiz), 3)
        # Las secciones que pasaron a ser widgets ya no están en el markdown.
        self.assertNotIn('Cómo desarrollarla', g.contenido)
        self.assertNotIn('## Checklist', g.contenido)
        # Forma de cada pregunta del quiz.
        q = g.quiz[0]
        for campo in ('pregunta', 'opciones', 'correcta', 'explicacion'):
            self.assertIn(campo, q)
