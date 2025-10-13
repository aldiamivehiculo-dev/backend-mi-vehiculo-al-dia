# usuarios/forms.py

from django import forms
from django.contrib.auth.forms import UserChangeForm as BaseUserChangeForm
from .models import Usuario

class UsuarioCreationForm(forms.ModelForm):
    # Campo simple para la contraseña temporal
    password = forms.CharField(label='Contraseña Inicial', widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ('rut', 'nombre', 'email', 'rol', 'is_staff', 'is_superuser', 
                  'fecha_nacimiento', 'residencia', 'telefono', 'password')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class UsuarioChangeForm(BaseUserChangeForm):
    class Meta(BaseUserChangeForm.Meta):
        model = Usuario
        # Excluye los campos auto_now_add/auto_now para evitar el FieldError
        exclude = ('created_at', 'update_at')