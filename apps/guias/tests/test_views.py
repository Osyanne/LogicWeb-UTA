from django.test import TestCase
from django.urls import reverse

from apps.guias.models import Guia


class GuiaListViewTest(TestCase):
    def test_lista_carga_publica(self):
        resp = self.client.get(reverse('guias_lista'))
        self.assertEqual(resp.status_code, 200)   # sin login (a diferencia de Mi Progreso)

    def test_muestra_publicadas_oculta_borradores(self):
        Guia.objects.create(codigo='C1', titulo='Guía Visible', slug='vis',
                            contenido='x', publicada=True)
        Guia.objects.create(codigo='C2', titulo='Guía Borrador', slug='bor',
                            contenido='x', publicada=False)
        resp = self.client.get(reverse('guias_lista'))
        self.assertContains(resp, 'Guía Visible')
        self.assertNotContains(resp, 'Guía Borrador')


class GuiaDetailViewTest(TestCase):
    def setUp(self):
        self.guia = Guia.objects.create(
            codigo='SW-AyLP-APE-99', titulo='Prueba', slug='ape-99',
            contenido='## Sub\n\nTexto con `cod`.',
            repo_url='https://github.com/x/y', pdf='guias/ape-04.pdf',
            publicada=True,
        )

    def test_detalle_por_slug(self):
        resp = self.client.get(reverse('guias_detalle', args=['ape-99']))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Prueba')

    def test_markdown_renderizado(self):
        resp = self.client.get(reverse('guias_detalle', args=['ape-99']))
        self.assertContains(resp, '<h2>Sub</h2>')
        self.assertContains(resp, '<code>cod</code>')

    def test_botones_pdf_y_repo(self):
        resp = self.client.get(reverse('guias_detalle', args=['ape-99']))
        self.assertContains(resp, 'Descargar PDF oficial')
        self.assertContains(resp, 'github.com/x/y')

    def test_404_si_no_publicada(self):
        Guia.objects.create(codigo='B', titulo='Oculta', slug='oculta',
                            contenido='x', publicada=False)
        resp = self.client.get(reverse('guias_detalle', args=['oculta']))
        self.assertEqual(resp.status_code, 404)

    def test_404_si_no_existe(self):
        resp = self.client.get(reverse('guias_detalle', args=['no-hay']))
        self.assertEqual(resp.status_code, 404)


class NavLinkTest(TestCase):
    def test_enlace_guias_en_nav(self):
        resp = self.client.get(reverse('inicio'))
        self.assertContains(resp, reverse('guias_lista'))
        self.assertContains(resp, 'Guías APE')
