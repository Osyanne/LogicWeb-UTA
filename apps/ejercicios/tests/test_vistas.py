from django.test import TestCase
from django.urls import reverse

from apps.ejercicios.models import Usuario, Notificacion


class ContextProcessorTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(username='est', password='clave12345')

    def test_conteo_no_leidas(self):
        Notificacion.objects.create(usuario=self.user, tipo='volumen', clave='volumen_10',
                                    titulo='x', mensaje='y', icono='trending-up', leida=False)
        self.client.force_login(self.user)
        resp = self.client.get(reverse('inicio'))
        self.assertEqual(resp.context['noti_no_leidas'], 1)

    def test_anonimo_no_rompe(self):
        resp = self.client.get(reverse('inicio'))
        self.assertEqual(resp.status_code, 200)


class NotificacionesVistaTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create_user(username='est', password='clave12345')

    def test_requiere_login(self):
        resp = self.client.get(reverse('notificaciones'))
        self.assertEqual(resp.status_code, 302)

    def test_pagina_carga_y_marca_leidas(self):
        Notificacion.objects.create(usuario=self.user, tipo='volumen', clave='volumen_10',
                                    titulo='¡10 ejercicios!', mensaje='y', icono='trending-up', leida=False)
        self.client.force_login(self.user)
        resp = self.client.get(reverse('notificaciones'))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, '¡10 ejercicios!')
        self.assertContains(resp, '<svg')  # el ícono se renderiza como SVG (no como emoji)
        self.assertEqual(Notificacion.objects.filter(usuario=self.user, leida=False).count(), 0)
