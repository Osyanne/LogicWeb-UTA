from django.test import TestCase
from django.urls import reverse

from apps.ejercicios.models import Usuario, Notificacion


class ContextProcessorTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(username='est', password='clave12345')

    def test_conteo_no_leidas(self):
        Notificacion.objects.create(usuario=self.user, tipo='volumen', clave='volumen_10',
                                    titulo='x', mensaje='y', icono='📈', leida=False)
        self.client.force_login(self.user)
        resp = self.client.get(reverse('inicio'))
        self.assertEqual(resp.context['noti_no_leidas'], 1)

    def test_anonimo_no_rompe(self):
        resp = self.client.get(reverse('inicio'))
        self.assertEqual(resp.status_code, 200)
