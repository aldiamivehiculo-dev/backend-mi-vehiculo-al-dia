from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from accesos.models import SharedAccess
from vehiculos.models import Vehiculo
from .serializers import VehiculoFiscalizadorSerializer, FiscalizacionSerializer
from .models import Fiscalizacion
from fiscalizador.permissions import IsFiscalizador
from documentos_vehiculo.models import DocumentoVehicular
from django.http import FileResponse

# Create your views here.

class FiscalizadorScanQR(APIView):
    permission_classes = [IsAuthenticated, IsFiscalizador]

    def get(self, request, token):
        shared = SharedAccess.objects.filter(token=token).first()

        if not shared or not shared.is_valid:
            return Response({"detail": "Token inválido o expirado"}, status=403)

        vehiculo = shared.vehiculo
        data = VehiculoFiscalizadorSerializer(vehiculo).data
        
        # marcar acceso como fiscalizador en logs
        shared.access_logs.create(
            usuario=request.user,
            is_prestamo=shared.is_prestamo,
            ip=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT")
        )

        return Response(data)

class FiscalizadorHistorial(APIView):
    permission_classes = [IsAuthenticated, IsFiscalizador]

    def get(self, request, vehiculo_id):
        vehiculo = Vehiculo.objects.filter(id=vehiculo_id).first()
        if not vehiculo:
            return Response({"detail": "Vehículo no encontrado"}, status=404)

        data = VehiculoFiscalizadorSerializer(vehiculo).data
        return Response(data)

class RegistrarFiscalizacion(APIView):
    permission_classes = [IsAuthenticated, IsFiscalizador]

    def post(self, request):
        ser = FiscalizacionSerializer(data=request.data)

        if not ser.is_valid():
            return Response(ser.errors, status=400)

        vehiculo = ser.validated_data["vehiculo"]

        # Validar que el fiscalizador NO fiscalice otro vehículo diferente al del QR
        token = request.query_params.get("token")
        if token:
            shared = SharedAccess.objects.filter(token=token).first()
            if shared and shared.vehiculo != vehiculo:
                return Response(
                    {"detail": "El vehículo no corresponde al token escaneado."},
                    status=400
                )

        ser.save(fiscalizador=request.user)
        return Response(ser.data, status=201)

class HistorialFiscalizacionesView(APIView):

    permission_classes = [IsAuthenticated, IsFiscalizador]

    def get(self, request, vehiculo_id):
        Fiscalizaciones = Fiscalizacion.objects.filter(vehiculo_id=vehiculo_id).order_by("-fecha")

        data = [{
            "id": f.id,
            "fecha": f.fecha,
            "observacion": f.observacion,
            "fiscalizador": {
                "rut": f.fiscalizador.rut if f.fiscalizador else None,
                "nombre": f.fiscalizador.nombre if f.fiscalizador else None
            }
        }
        for f in    Fiscalizaciones
        ]
        return Response(data)
    
class FiscalizadorQRLogs(APIView):
    permission_classes = [IsAuthenticated, IsFiscalizador]

    def get(self, request, token):
        shared = SharedAccess.objects.filter(token=token).first()

        if not shared:
            return Response({"detail": "Token no encontrado"}, status=404)

        logs = shared.access_logs.all().order_by("-accessed_at")

        data = [
            {
                "fecha": log.accessed_at,
                "ip": log.ip,
                "user_agent": log.user_agent,
                "tipo_acceso": "préstamo" if log.is_prestamo else "fiscalización",
                "usuario_rut": log.usuario.rut if log.usuario else None,
            }
            for log in logs
        ]

        return Response(data)

class FiscalizadorVerPDF(APIView):
    permission_classes = [IsAuthenticated, IsFiscalizador]

    def get(self, request, doc_id):
        doc = DocumentoVehicular.objects.filter(id=doc_id).first()

        if not doc:
            return Response({"detail": "Documento no encontrado"}, status=404)

        if not doc.archivo:
            return Response({"detail": "Documento sin archivo"}, status=404)

        return FileResponse(
            doc.archivo.open('rb'),
            content_type='application/pdf'
        )
