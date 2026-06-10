from django.test import SimpleTestCase

from apps.guias.templatetags.guias_extras import markdownify


class MarkdownifyTest(SimpleTestCase):
    def test_encabezado(self):
        self.assertIn('<h2>Hola</h2>', markdownify('## Hola'))

    def test_fenced_code_con_lenguaje(self):
        html = markdownify('```java\nint x = 1;\n```')
        self.assertIn('language-java', html)   # highlight.js usa esta clase

    def test_tabla(self):
        html = markdownify('| a | b |\n|---|---|\n| 1 | 2 |')
        self.assertIn('<table>', html)

    def test_vacio_no_rompe(self):
        self.assertEqual(markdownify(''), '')
