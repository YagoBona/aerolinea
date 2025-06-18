from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario
from django.contrib.auth.forms import AuthenticationForm

class FormularioRegistro(UserCreationForm):
    dni = forms.CharField(label="DNI", max_length=20, required=True)

    class Meta:
        model = Usuario
        fields = ['username', 'email', 'dni', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(FormularioRegistro, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

class FormularioLogin(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(FormularioLogin, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'