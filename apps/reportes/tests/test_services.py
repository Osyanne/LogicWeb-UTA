from django.test import TestCase

from apps.ejercicios.models import Usuario, Tema, Ejercicio, Intento
from apps.reportes import services


class ProgresoEstudianteServiceTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(username='est', password='clave12345')
        self.tema = Tema.objects.create(
            nombre_tema='Algoritmos', descripcion='x', unidad=1, orden=1,
        )
        self.ej1 = Ejercicio.objects.create(
            titulo='Suma', enunciado='e', categoria='interactivo', tema=self.tema,
            codigo_cpp='int main(){}', solucion_esperada='5', tipo_respuesta='entero',
        )
        self.ej2 = Ejercicio.objects.create(
            titulo='Resta', enunciado='e', categoria='resuelto', tema=self.tema,
            codigo_cpp='', solucion_esperada='2', tipo_respuesta='entero',
        )

    def test_sin_intentos(self):
        data = services.progreso_estudiante(self.user)
        self.assertEqual(data['total'], 0)
        self.assertEqual(data['correctos'], 0)
        self.assertEqual(data['incorrectos'], 0)
        self.assertEqual(data['porcentaje'], 0)
        self.assertEqual(data['codigos_vistos'], 0)
        self.assertEqual(data['progreso_unidades'], [])
        self.assertEqual(data['intentos'], [])

    def test_cuenta_y_porcentaje(self):
        Intento.objects.create(usuario=self.user, ejercicio=self.ej1, respuesta_usuario='5', resultado='correcto')
        Intento.objects.create(usuario=self.user, ejercicio=self.ej1, respuesta_usuario='9', resultado='incorrecto')
        Intento.objects.create(usuario=self.user, ejercicio=self.ej2, respuesta_usuario='2', resultado='correcto')

        data = services.progreso_estudiante(self.user)
        self.assertEqual(data['total'], 3)
        self.assertEqual(data['correctos'], 2)
        self.assertEqual(data['incorrectos'], 1)
        self.assertEqual(data['porcentaje'], 67)          # round(2/3*100)
        self.assertEqual(data['codigos_vistos'], 1)        # solo ej1 tiene codigo_cpp no vacío

    def test_progreso_unidades_e_intentos(self):
        Intento.objects.create(usuario=self.user, ejercicio=self.ej1, respuesta_usuario='5', resultado='correcto')

        data = services.progreso_estudiante(self.user)
        # el signal post_save creó ProgresoEstudiante para la unidad 1
        self.assertEqual(len(data['progreso_unidades']), 1)
        u = data['progreso_unidades'][0]
        self.assertEqual(u['unidad'], 1)
        self.assertEqual(u['total'], 1)
        self.assertEqual(u['correctos'], 1)
        self.assertEqual(u['porcentaje'], 100)
        self.assertEqual(u['nombre'], dict(Tema.UNIDADES)[1])

        self.assertEqual(len(data['intentos']), 1)
        it = data['intentos'][0]
        self.assertEqual(it['titulo'], 'Suma')
        self.assertEqual(it['unidad'], 1)
        self.assertEqual(it['tema'], 'Algoritmos')
        self.assertEqual(it['categoria'], 'interactivo')
        self.assertEqual(it['categoria_display'], 'Ejercicio Interactivo')
        self.assertTrue(it['codigo_visto'])
        self.assertEqual(it['resultado'], 'correcto')
