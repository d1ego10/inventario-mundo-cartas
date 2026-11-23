from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from .models import Rol

class CrearUsuarioForm(UserCreationForm):
    rol = forms.ModelChoiceField(
        queryset=Rol.objects.filter(
            nombre__in=["Administrador", "Vendedor"]
        ),
        empty_label="Selecciona un rol",
        label="Rol",
    )

    class Meta:
        model = get_user_model()
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "rol",
            "password1",
            "password2",
        )
        labels = {
            "username": "Nombre de usuario",
            "first_name": "Nombre",
            "last_name": "Apellido",
            "email": "Correo electrónico",
        }