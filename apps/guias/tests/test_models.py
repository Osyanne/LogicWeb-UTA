from django.db import IntegrityError, transaction
from django.test import TestCase

from apps.guias.models import Guia


class GuiaModelTest(TestCase):
    def _crear(self, **kw):
        datos = dict(codigo='SW-AyLP-APE-01', titulo='Intro',
                     slug='ape-01', contenido='# Hola')
        datos.update(kw)
        return Guia.objects.create(**datos)

    def test_str(self):
        g = self._crear()
        self.assertEqual(str(g), 'SW-AyLP-APE-01 — Intro')

    def test_publicada_por_defecto(self):
        self.assertTrue(self._crear().publicada)

    def test_slug_unico(self):
        self._crear(slug='dup')
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self._crear(codigo='X', titulo='Y', slug='dup')

    def test_ordering_por_orden(self):
        self._crear(slug='b', codigo='B', orden=2)
        self._crear(slug='a', codigo='A', orden=1)
        ordenes = list(
            Guia.objects.filter(slug__in=['a', 'b']).values_list('orden', flat=True)
        )
        self.assertEqual(ordenes, [1, 2])


class GuiaAdminTest(TestCase):
    def test_registrado_en_admin(self):
        from django.contrib import admin
        self.assertTrue(admin.site.is_registered(Guia))
