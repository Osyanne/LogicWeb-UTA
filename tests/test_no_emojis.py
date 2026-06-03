import re
import pytest
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
EMOJI_RE = re.compile('[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U00002B00-\U00002BFF]')

def emojis_in(rel):
    return EMOJI_RE.findall((ROOT / rel).read_text(encoding="utf-8"))

def test_no_emoji_base_and_theme():
    assert emojis_in("templates/base.html") == []
    assert emojis_in("static/js/theme.js") == []

def test_no_emoji_inicio():
    assert emojis_in("templates/inicio/index.html") == []

def test_no_emoji_auth():
    assert emojis_in("templates/usuarios/login.html") == []
    assert emojis_in("templates/usuarios/registro.html") == []

def test_no_emoji_progreso():
    assert emojis_in("templates/reportes/mi_progreso.html") == []

def test_no_emoji_contenidos():
    assert emojis_in("templates/contenidos/lista.html") == []
    assert emojis_in("templates/contenidos/detalle.html") == []

def test_no_emoji_comparar():
    assert emojis_in("templates/comparaciones/comparar.html") == []
    assert emojis_in("apps/ejercicios/comparaciones.py") == []

def test_no_emoji_resueltos():
    assert emojis_in("templates/ejercicios/resuelto.html") == []
    assert emojis_in("templates/ejercicios/lista_resueltos.html") == []

def test_no_emoji_interactivos():
    assert emojis_in("templates/ejercicios/interactivo.html") == []
    assert emojis_in("templates/ejercicios/lista_interactivos.html") == []

def test_no_emoji_respuesta():
    assert emojis_in("templates/retroalimentacion/respuesta.html") == []

IN_SCOPE = [
    "templates/base.html","templates/inicio/index.html",
    "templates/usuarios/login.html","templates/usuarios/registro.html",
    "templates/contenidos/lista.html","templates/contenidos/detalle.html",
    "templates/comparaciones/comparar.html","templates/retroalimentacion/respuesta.html",
    "templates/reportes/mi_progreso.html","templates/ejercicios/interactivo.html",
    "templates/ejercicios/resuelto.html","templates/ejercicios/lista_resueltos.html",
    "templates/ejercicios/lista_interactivos.html","static/js/theme.js",
    "apps/ejercicios/comparaciones.py",
]

@pytest.mark.parametrize("rel", IN_SCOPE)
def test_no_decorative_emoji_anywhere(rel):
    assert emojis_in(rel) == [], f"quedó un emoji en {rel}"
