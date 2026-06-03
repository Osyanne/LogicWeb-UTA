import re
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
