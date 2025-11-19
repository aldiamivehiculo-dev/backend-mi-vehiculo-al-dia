from django.urls import path
from .views import FiscalizadorScanQR, FiscalizadorHistorial, RegistrarFiscalizacion, HistorialFiscalizacionesView, FiscalizadorQRLogs, FiscalizadorVerPDF

urlpatterns = [
    path("scan/<str:token>/", FiscalizadorScanQR.as_view()),
    path("vehiculo/<int:vehiculo_id>/", FiscalizadorHistorial.as_view(), name="fiscalizador-vehiculo"),
    path("registrar/", RegistrarFiscalizacion.as_view()),
    path("fiscalizaciones/<int:vehiculo_id>/", HistorialFiscalizacionesView.as_view(), name="fiscalizaciones-vehiculo"),
    path("qr/logs/<str:token>/", FiscalizadorQRLogs.as_view(), name="fiscalizador-qr-logs"),
    path("pdf/<int:doc_id>/", FiscalizadorVerPDF.as_view(), name="fiscalizador-pdf"),
]

#2) Agregar la hoja (view) del fiscalizador en la App Ionic