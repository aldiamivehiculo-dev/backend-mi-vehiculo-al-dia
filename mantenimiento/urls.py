from django.urls import path
from .views import RegistrarMantenimientoView, ListarMantenimientosView, ActualizarMantenimientoView, EliminarMantenimientoView
urlpatterns = [
        path("registrar/", RegistrarMantenimientoView.as_view()),
        path("listar/", ListarMantenimientosView.as_view()),
        path("actualizar/<int:pk>/", ActualizarMantenimientoView.as_view()),
        path("eliminar/<int:pk>/", EliminarMantenimientoView.as_view()),
    ]
