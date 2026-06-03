from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
ICONS = ["code","bar-chart","layers","log-in","user-plus","route","terminal",
         "book","book-open","check-circle","x-circle","alert-triangle","x"]

def test_all_icon_partials_exist_and_are_svg():
    icondir = ROOT / "templates" / "icons"
    for name in ICONS:
        f = icondir / f"{name}.svg"
        assert f.exists(), f"falta {f}"
        s = f.read_text(encoding="utf-8")
        assert "<svg" in s and "</svg>" in s, f"{name}.svg no es SVG válido"
        assert 'stroke="currentColor"' in s, f"{name}.svg debe usar currentColor"
