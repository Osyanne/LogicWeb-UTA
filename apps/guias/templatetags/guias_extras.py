import markdown as md
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name='markdownify')
def markdownify(texto):
    """Convierte Markdown (fuente confiable: solo staff edita guías) a HTML.

    `fenced_code` emite <pre><code class="language-xxx"> que highlight.js colorea.
    """
    if not texto:
        return ''
    html = md.markdown(texto, extensions=['fenced_code', 'tables'])
    return mark_safe(html)
