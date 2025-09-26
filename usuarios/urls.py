from django.urls import path
from .views import RegistroUsuarioView, RecuperarContrasenaView, CambiarContrasenaView

urlpatterns = [
    path('registro/', RegistroUsuarioView.as_view(), name='registro-usuario'),
    path('recuperar-contrasena/', RecuperarContrasenaView.as_view(), name='recuperar-contrasena'),
    path('cambiar-password/', CambiarContrasenaView.as_view(), name='cambiar-password')

]
    