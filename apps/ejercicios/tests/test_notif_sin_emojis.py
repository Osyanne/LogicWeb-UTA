"""
Guard local: los archivos de la feature de notificaciones no deben contener emojis.

Replica el criterio del test anti-emoji del proyecto (rango pictográfico Unicode)
sobre los archivos que esta feature controla por completo. Mantiene notificaciones
alineada con la política "íconos SVG, no emojis".

NOTA: no se escanea `templates/base.html` aquí porque ese archivo tiene contenido
de otras zonas del navbar (marca, usuario) que limpia el sub-proyecto de íconos.
"""
import re
from pathlib import Path

from django.test import SimpleTestCase

ROOT = Path(__file__).resolve().parents[3]  # .../proyecto_django
EMOJI_RE = re.compile('[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U00002B00-\U00002BFF]')

ARCHIVOS_NOTIF = [
    'apps/ejercicios/logros.py',
    'apps/ejercicios/models.py',
    'templates/notificaciones/lista.html',
    'static/js/notificaciones.js',
    'static/css/notificaciones.css',
]


class NotifSinEmojisTest(SimpleTestCase):
    def test_archivos_de_notificaciones_sin_emojis(self):
        for rel in ARCHIVOS_NOTIF:
            contenido = (ROOT / rel).read_text(encoding='utf-8')
            emojis = EMOJI_RE.findall(contenido)
            self.assertEqual(emojis, [], f'quedó un emoji en {rel}: {emojis}')
