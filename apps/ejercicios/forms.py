# RegistroForm movido a apps/usuarios/forms.py

from django import forms


# ── Respuesta de ejercicio interactivo ───────────────────────
class RespuestaForm(forms.Form):
    respuesta = forms.CharField(
        max_length=200,
        label='Tu respuesta',
        widget=forms.TextInput(attrs={
            'placeholder': 'Escribe aquí tu respuesta...',
            'autocomplete': 'off',
            'class': 'input-respuesta',
        })
    )

    def clean_respuesta(self):
        resp = self.cleaned_data.get('respuesta', '').strip()
        if not resp:
            raise forms.ValidationError('Debes escribir una respuesta antes de verificar.')
        return resp
