from django.test import TestCase

from apps.ejercicios.models import Usuario, Tema, Ejercicio, Intento, Notificacion


class SignalLogrosTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(username='est', password='clave12345')
        self.tema = Tema.objects.create(nombre_tema='Lógica', descripcion='t', unidad=1)
        self.ej = Ejercicio.objects.create(
            titulo='Suma', enunciado='2+3', categoria='interactivo', tema=self.tema,
            lenguaje='cpp', codigo_cpp='//', solucion_esperada='5', tipo_respuesta='entero',
        )

    def test_intento_correcto_dispara_notificacion(self):
        Intento.objects.create(usuario=self.user, ejercicio=self.ej,
                               respuesta_usuario='5', resultado='correcto')
        self.assertTrue(
            Notificacion.objects.filter(usuario=self.user, clave='primer_correcto').exists())

    def test_intento_incorrecto_no_dispara(self):
        Intento.objects.create(usuario=self.user, ejercicio=self.ej,
                               respuesta_usuario='9', resultado='incorrecto')
        self.assertEqual(Notificacion.objects.filter(usuario=self.user).count(), 0)
