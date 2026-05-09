from django import forms
from django.contrib.auth.forms import UserCreationForm

from apps.ejercicios.models import Usuario


class RegistroForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True, label='Nombre')
    last_name  = forms.CharField(max_length=50, required=True, label='Apellido')
    email      = forms.EmailField(required=True, label='Correo electrónico')

    class Meta:
        model  = Usuario
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError('Ya existe una cuenta con ese correo electrónico.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.rol   = 'estudiante'
        if commit:
            user.save()
        return user
