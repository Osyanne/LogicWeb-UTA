from django.test import TestCase
from django.core.management import call_command

from apps.ejercicios.models import Usuario, Tema, Ejercicio, Intento, ProgresoEstudiante


class CrearDemoCommandTest(TestCase):
    def _crear_ejercicio(self):
        tema = Tema.objects.create(nombre_tema='T1', descripcion='x', unidad=1, orden=1)
        return Ejercicio.objects.create(
            titulo='Suma', enunciado='e', categoria='interactivo',
            tema=tema, codigo_cpp='x', solucion_esperada='4', tipo_respuesta='entero',
        )

    def test_crea_usuario_demo_idempotente(self):
        self._crear_ejercicio()
        call_command('crear_demo')
        call_command('crear_demo')  # 2da corrida no debe duplicar

        demos = Usuario.objects.filter(username='demo')
        self.assertEqual(demos.count(), 1)
        demo = demos.first()
        self.assertEqual(demo.rol, 'estudiante')
        self.assertTrue(demo.check_password('Demo123*'))

    def test_siembra_progreso_sin_duplicar(self):
        self._crear_ejercicio()  # 1 ejercicio en la unidad 1
        call_command('crear_demo')
        call_command('crear_demo')

        demo = Usuario.objects.get(username='demo')
        self.assertEqual(Intento.objects.filter(usuario=demo).count(), 1)
        self.assertTrue(
            ProgresoEstudiante.objects.filter(usuario=demo, unidad=1, correctos__gte=1).exists()
        )
