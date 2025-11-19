from django.urls import path
from .views import NotificacionListView,NotificacionMarcarLeidaView,NotificacionMarcarTodasLeidasView
urlpatterns = [
    path("", NotificacionListView.as_view(), name="notificaciones-listar"),
    path("<int:pk>/leer/", NotificacionMarcarLeidaView.as_view(), name="notificacion-leer"),
    path("leer-todas/", NotificacionMarcarTodasLeidasView.as_view(), name="notificaciones-leer-todas"),
]
