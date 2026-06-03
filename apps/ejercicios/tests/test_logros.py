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


class VolumenTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(username='est', password='clave12345')
        self.tema = Tema.objects.create(nombre_tema='Lógica', descripcion='t', unidad=1)

    def _resolver_n_distintos(self, n):
        ejercicios = [crear_ejercicio(self.tema, titulo=f'Ej{i}') for i in range(n)]
        Intento.objects.bulk_create([
            Intento(usuario=self.user, ejercicio=ej, respuesta_usuario='1', resultado='correcto')
            for ej in ejercicios
        ])

    def test_volumen_10_se_otorga_con_10(self):
        self._resolver_n_distintos(10)
        otorgar_logros(self.user)
        self.assertTrue(Notificacion.objects.filter(usuario=self.user, clave='volumen_10').exists())

    def test_volumen_10_no_con_9(self):
        self._resolver_n_distintos(9)
        otorgar_logros(self.user)
        self.assertFalse(Notificacion.objects.filter(usuario=self.user, clave='volumen_10').exists())

    def test_volumen_cuenta_distintos_no_reintentos(self):
        ej = crear_ejercicio(self.tema)
        Intento.objects.bulk_create([
            Intento(usuario=self.user, ejercicio=ej, respuesta_usuario='1', resultado='correcto')
            for _ in range(10)
        ])
        otorgar_logros(self.user)
        self.assertFalse(Notificacion.objects.filter(usuario=self.user, clave='volumen_10').exists())


class UnidadesTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(username='est', password='clave12345')
        self.tema = Tema.objects.create(nombre_tema='Lógica', descripcion='t', unidad=1)

    def _resolver(self, ej):
        Intento.objects.bulk_create([
            Intento(usuario=self.user, ejercicio=ej, respuesta_usuario='1', resultado='correcto')
        ])

    def test_unidad_completa_se_otorga(self):
        e1 = crear_ejercicio(self.tema, titulo='A')
        e2 = crear_ejercicio(self.tema, titulo='B')
        self._resolver(e1)
        self._resolver(e2)
        otorgar_logros(self.user)
        self.assertTrue(Notificacion.objects.filter(usuario=self.user, clave='unidad_1').exists())

    def test_unidad_incompleta_no_se_otorga(self):
        e1 = crear_ejercicio(self.tema, titulo='A')
        crear_ejercicio(self.tema, titulo='B')  # existe pero no se resuelve
        self._resolver(e1)
        otorgar_logros(self.user)
        self.assertFalse(Notificacion.objects.filter(usuario=self.user, clave='unidad_1').exists())

    def test_resueltos_no_inflan_el_total(self):
        inter = crear_ejercicio(self.tema, titulo='Inter', categoria='interactivo')
        crear_ejercicio(self.tema, titulo='Resu', categoria='resuelto')  # no cuenta para el total
        self._resolver(inter)
        otorgar_logros(self.user)
        self.assertTrue(Notificacion.objects.filter(usuario=self.user, clave='unidad_1').exists())
