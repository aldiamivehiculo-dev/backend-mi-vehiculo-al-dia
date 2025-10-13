from django.urls import path
from .views import RegistroUsuarioView, RecuperarContrasenaView, CambiarContrasenaView, UsuarioPerfilView, EliminarCuentaView

urlpatterns = [
    path('registro/', RegistroUsuarioView.as_view(), name='registro-usuario'),
    path('recuperar-contrasena/', RecuperarContrasenaView.as_view(), name='recuperar-contrasena'),
    path('cambiar-password/', CambiarContrasenaView.as_view(), name='cambiar-password'),
    path('perfil/', UsuarioPerfilView.as_view(), name='perfil'),
    path('eliminar-cuenta/', EliminarCuentaView.as_view(), name='eliminar-cuenta'),

]
    