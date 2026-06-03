from django.test import TestCase

from apps.ejercicios.models import Usuario, Tema, Ejercicio, Intento, Notificacion
from apps.ejercicios.logros import otorgar_logros


def crear_ejercicio(tema, lenguaje='cpp', categoria='interactivo', titulo='Ej'):
    return Ejercicio.objects.create(
        titulo=titulo, enunciado='enunciado', categoria=categoria, tema=tema,
        lenguaje=lenguaje, codigo_cpp='// code', solucion_esperada='1', tipo_respuesta='entero',
    )


class PrimerosPasosTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(username='est', password='clave12345')
        self.tema = Tema.objects.create(nombre_tema='Lógica', descripcion='t', unidad=1)

    def _resolver(self, ejercicio):
        # intento correcto SIN disparar el signal (bulk_create no llama post_save)
        Intento.objects.bulk_create([
            Intento(usuario=self.user, ejercicio=ejercicio, respuesta_usuario='1', resultado='correcto')
        ])

    def test_primer_correcto_se_otorga(self):
        self._resolver(crear_ejercicio(self.tema, lenguaje='cpp'))
        otorgar_logros(self.user)
        self.assertTrue(Notificacion.objects.filter(usuario=self.user, clave='primer_correcto').exists())

    def test_primer_lenguaje_se_otorga(self):
        self._resolver(crear_ejercicio(self.tema, lenguaje='java'))
        otorgar_logros(self.user)
        self.assertTrue(Notificacion.objects.filter(usuario=self.user, clave='primer_java').exists())

    def test_no_duplica(self):
        self._resolver(crear_ejercicio(self.tema, lenguaje='cpp'))
        otorgar_logros(self.user)
        otorgar_logros(self.user)
        self.assertEqual(
            Notificacion.objects.filter(usuario=self.user, clave='primer_correcto').count(), 1)

    def test_ver_resuelto_no_cuenta(self):
        self._resolver(crear_ejercicio(self.tema, categoria='resuelto'))
        otorgar_logros(self.user)
        self.assertFalse(Notificacion.objects.filter(usuario=self.user, clave='primer_correcto').exists())
