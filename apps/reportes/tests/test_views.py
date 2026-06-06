from django.test import TestCase
from django.urls import reverse

from apps.ejercicios.models import Usuario, Tema, Ejercicio, Intento


class MiProgresoViewTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(username='est', password='clave12345')

    def test_requiere_login(self):
        resp = self.client.get(reverse('mi_progreso'))
        self.assertEqual(resp.status_code, 302)

    def test_carga_ok(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse('mi_progreso'))
        self.assertEqual(resp.status_code, 200)

    def test_historial_muestra_intento(self):
        tema = Tema.objects.create(nombre_tema='Algoritmos', descripcion='x', unidad=1, orden=1)
        ej = Ejercicio.objects.create(
            titulo='Suma', enunciado='e', categoria='interactivo', tema=tema,
            codigo_cpp='x', solucion_esperada='5', tipo_respuesta='entero',
        )
        Intento.objects.create(usuario=self.user, ejercicio=ej, respuesta_usuario='5', resultado='correcto')
        self.client.force_login(self.user)
        resp = self.client.get(reverse('mi_progreso'))
        self.assertContains(resp, 'Suma')
        self.assertContains(resp, '<svg')   # iconos SVG, no emojis

    def test_muestra_botones_export_y_datos_grafico(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse('mi_progreso'))
        self.assertContains(resp, reverse('exportar_pdf'))
        self.assertContains(resp, reverse('exportar_excel'))
        self.assertContains(resp, 'id="datos-progreso"')        # json_script de Chart.js

    def test_canvas_aparece_con_intentos(self):
        tema = Tema.objects.create(nombre_tema='Algoritmos', descripcion='x', unidad=1, orden=1)
        ej = Ejercicio.objects.create(
            titulo='Suma', enunciado='e', categoria='interactivo', tema=tema,
            codigo_cpp='x', solucion_esperada='5', tipo_respuesta='entero',
        )
        Intento.objects.create(usuario=self.user, ejercicio=ej, respuesta_usuario='5', resultado='correcto')
        self.client.force_login(self.user)
        resp = self.client.get(reverse('mi_progreso'))
        self.assertContains(resp, 'id="grafico-unidades"')
        self.assertContains(resp, 'id="grafico-aciertos"')
        self.assertContains(resp, 'reportes_charts.js')
