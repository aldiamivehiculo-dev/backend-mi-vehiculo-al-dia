from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
# Register your models here
#clase admin
class UsuarioAdmin(BaseUserAdmin):
    # Campos que se muestran en la lista del admin
    list_display = ('rut', 'nombre', 'email', 'rol', 'is_staff', 'is_superuser')
    list_filter = ('rol', 'is_staff', 'is_superuser', 'is_active')
    ordering = ('rut',)  # campo por el que se ordena
    search_fields = ('rut', 'nombre', 'email')

    # Campos que se muestran en el formulario de edición
    fieldsets = (
        (None, {'fields': ('rut', 'password')}),
        (_('Información personal'), {'fields': ('nombre', 'email', 'fecha_nacimiento', 'residencia', 'telefono')}),
        (_('Permisos'), {'fields': ('rol', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Fechas importantes'), {'fields': ('last_login', 'created_at', 'update_at')}),
    )

    # Campos que se muestran al crear un usuario desde el admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('rut', 'nombre', 'email', 'password1', 'password2', 'rol', 'is_staff', 'is_superuser'),
        }),
    )

admin.site.register(Usuario, UsuarioAdmin)
