from django.test import TestCase

from apps.ejercicios.models import Usuario, Tema, Ejercicio, Intento
from apps.reportes import services, exporters


def _data(user):
    return services.progreso_estudiante(user)


class ExcelExporterTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            username='est', password='clave12345', first_name='Ana', last_name='Pérez',
        )
        tema = Tema.objects.create(nombre_tema='Algoritmos', descripcion='x', unidad=1, orden=1)
        ej = Ejercicio.objects.create(
            titulo='Suma', enunciado='e', categoria='interactivo', tema=tema,
            codigo_cpp='x', solucion_esperada='5', tipo_respuesta='entero',
        )
        Intento.objects.create(usuario=self.user, ejercicio=ej, respuesta_usuario='5', resultado='correcto')

    def test_excel_es_xlsx(self):
        contenido = exporters.reporte_estudiante_excel(_data(self.user), self.user)
        self.assertIsInstance(contenido, bytes)
        self.assertTrue(contenido.startswith(b'PK'))     # magic de zip/xlsx
        self.assertGreater(len(contenido), 1000)

    def test_excel_estudiante_sin_intentos(self):
        vacio = Usuario.objects.create_user(username='vacio', password='clave12345')
        contenido = exporters.reporte_estudiante_excel(_data(vacio), vacio)
        self.assertTrue(contenido.startswith(b'PK'))


class PdfExporterTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            username='est', password='clave12345', first_name='Ana', last_name='Pérez',
        )
        tema = Tema.objects.create(nombre_tema='Algoritmos', descripcion='x', unidad=1, orden=1)
        ej = Ejercicio.objects.create(
            titulo='Suma', enunciado='e', categoria='interactivo', tema=tema,
            codigo_cpp='x', solucion_esperada='5', tipo_respuesta='entero',
        )
        Intento.objects.create(usuario=self.user, ejercicio=ej, respuesta_usuario='5', resultado='correcto')

    def test_pdf_es_pdf(self):
        contenido = exporters.reporte_estudiante_pdf(_data(self.user), self.user)
        self.assertIsInstance(contenido, bytes)
        self.assertTrue(contenido.startswith(b'%PDF'))
        self.assertGreater(len(contenido), 1000)

    def test_pdf_estudiante_sin_intentos(self):
        vacio = Usuario.objects.create_user(username='vacio', password='clave12345')
        contenido = exporters.reporte_estudiante_pdf(_data(vacio), vacio)
        self.assertTrue(contenido.startswith(b'%PDF'))


class ExcelContenidoTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(
            username='ana', password='clave12345', first_name='Ana', last_name='Pérez',
        )
        tema = Tema.objects.create(nombre_tema='Algoritmos', descripcion='x', unidad=1, orden=1)
        ej = Ejercicio.objects.create(
            titulo='Suma', enunciado='e', categoria='interactivo', tema=tema,
            codigo_cpp='x', solucion_esperada='5', tipo_respuesta='entero',
        )
        Intento.objects.create(usuario=self.user, ejercicio=ej, respuesta_usuario='5', resultado='correcto')

    def test_excel_hojas_y_contenido(self):
        import io
        from openpyxl import load_workbook
        contenido = exporters.reporte_estudiante_excel(_data(self.user), self.user)
        wb = load_workbook(io.BytesIO(contenido))
        self.assertEqual(wb.sheetnames, ['Resumen', 'Historial'])
        hist = wb['Historial']
        encabezado = [c.value for c in hist[1]]
        self.assertEqual(
            encabezado,
            ['Ejercicio', 'Unidad', 'Tema', 'Tipo', 'Tu respuesta', 'Resultado', 'Fecha'],
        )
        self.assertEqual(hist.cell(row=2, column=1).value, 'Suma')
        self.assertEqual(hist.cell(row=2, column=2).value, 'U1')
        self.assertEqual(hist.cell(row=2, column=6).value, 'correcto')
