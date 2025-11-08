# usuarios/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import Usuario 
from .forms import UsuarioCreationForm, UsuarioChangeForm 

class UsuarioAdmin(BaseUserAdmin):
    # Asignación de formularios (Soluciona E016)
    form = UsuarioChangeForm 
    add_form = UsuarioCreationForm 

    # Corrección de campos (Soluciona E003/E108)
    list_display = ('rut', 'nombre','apellidos', 'email', 'rol', 'is_staff', 'is_superuser')
    list_filter = ('rol', 'is_staff', 'is_superuser', 'is_active')
    ordering = ('rut',) 
    search_fields = ('rut', 'nombre', 'email') 

    readonly_fields = ('last_login', 'created_at', 'update_at') 

    fieldsets = (
        (None, {'fields': ('rut', 'password')}), 
        (_('Información personal'), {'fields': ('nombre','apellidos', 'email', 'fecha_nacimiento', 'residencia', 'telefono')}),
        (_('Permisos'), {'fields': ('rol', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Fechas importantes'), {'fields': ('last_login', 'created_at', 'update_at')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            # Incluye 'password' del formulario personalizado
            'fields': ('rut', 'nombre', 'apellidos', 'email', 'rol', 'is_staff', 'is_superuser', 'password'), 
        }),
        (_('Información personal adicional'), {'fields': ('fecha_nacimiento', 'residencia', 'telefono')}),
    )

admin.site.register(Usuario, UsuarioAdmin)