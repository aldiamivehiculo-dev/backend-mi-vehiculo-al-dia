from django.urls import path
from .views import (FiscalizadorScanQR,RegistrarFiscalizacion,HistorialFiscalizadorListView,HistorialFiscalizacionesView,FiscalizadorVerPDF)

urlpatterns = [
    # Escanear QR
    path("scan/<str:token>/", FiscalizadorScanQR.as_view(), name="fiscalizador-scan"),
    # Historial general del fiscalizador (lo que él fiscalizó)
    path("historial/", HistorialFiscalizadorListView.as_view(), name="fiscalizador-historial"),
    # Registrar una fiscalización
    path("registrar/", RegistrarFiscalizacion.as_view(), name="fiscalizador-registrar"),
    # Fiscalizaciones por vehículo
    path("vehiculo/<int:vehiculo_id>/", HistorialFiscalizacionesView.as_view(), name="fiscalizaciones-vehiculo"),
    # Ver un PDF
    path("pdf/<int:doc_id>/", FiscalizadorVerPDF.as_view(), name="fiscalizador-pdf"),
]
