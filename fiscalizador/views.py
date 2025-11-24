from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from accesos.models import SharedAccess
from vehiculos.models import Vehiculo
from documentos_vehiculo.models import DocumentoVehicular
from .models import Fiscalizacion
from .serializers import VehiculoFiscalizadorSerializer
from fiscalizador.permissions import IsFiscalizador
from django.http import FileResponse
from notificaciones.utils import crear_notificacion

#ESCANEAR QR (MOSTRAR DATOS)
class FiscalizadorScanQR(APIView):
    permission_classes = [IsAuthenticated, IsFiscalizador]

    def get(self, request, token):
        shared = SharedAccess.objects.filter(token=token).first()

        if not shared or not shared.is_valid:
            return Response({"detail": "Token inválido o expirado"}, status=403)

        vehiculo = shared.vehiculo
        data = VehiculoFiscalizadorSerializer(vehiculo).data

        # Registrar acceso del fiscalizador
        shared.access_logs.create(
            usuario=request.user,
            is_prestamo=shared.is_prestamo,
            ip=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT")
        )

        # Notificación al dueño del vehículo
        crear_notificacion(
            user=vehiculo.user,
            titulo="Vehículo fiscalizado",
            mensaje=f"Tu vehículo con patente {vehiculo.patente} ha sido fiscalizado por un inspector autorizado.",
            tipo="fiscalizacion",
            meta={
                "vehiculo_id": vehiculo.id,
                "patente": vehiculo.patente,
                "fecha": str(shared.expires_at)
            },
            send_email=False
        )

        return Response(data)

#HISTORIAL
class HistorialFiscalizadorListView(APIView):
    permission_classes = [IsAuthenticated, IsFiscalizador]

    def get(self, request):
        fiscalizador = request.user

        fiscalizaciones = Fiscalizacion.objects.filter(
            fiscalizador=fiscalizador
        ).order_by("-fecha")

        data = [{
            "id": f.id,
            "fecha": f.fecha,
            "vehiculo": {
                "patente": f.vehiculo.patente,
                "marca": f.vehiculo.marca,
            },
            "observacion": f.observacion,
        } for f in fiscalizaciones]

        return Response(data)

#REGISTRAR FISCALIZACIÓN
class RegistrarFiscalizacion(APIView):
    permission_classes = [IsAuthenticated, IsFiscalizador]

    def post(self, request):
        user = request.user
        token = request.data.get("token")
        vehiculo_id = request.data.get("vehiculo")
        advertencias = request.data.get("advertencias", [])

        #Validar rol
        if user.rol != "fiscalizador":
            return Response({"detail": "No autorizado."}, status=403)

        #Buscar vehículo
        try:
            vehiculo = Vehiculo.objects.get(id=vehiculo_id)
        except Vehiculo.DoesNotExist:
            return Response({"detail": "Vehículo no encontrado"}, status=404)

        #Crear registro de fiscalización
        registro = Fiscalizacion.objects.create(
            fiscalizador=user,
            vehiculo=vehiculo,
            token=token,
            advertencias=advertencias
        )

        #Notificación al usuario dueño
        crear_notificacion(
            user=vehiculo.user,
            titulo="Vehículo fiscalizado",
            mensaje=f"Tu vehículo con patente {vehiculo.patente} ha sido fiscalizado.",
            tipo="fiscalizacion",
            meta={
                "vehiculo_id": vehiculo.id,
                "patente": vehiculo.patente
            }
        )

        return Response({
            "mensaje": "Fiscalización registrada correctamente",
            "id": registro.id
        }, status=201)
    
#HISTORIAL SOLO FISCALIZACIONES
class HistorialFiscalizacionesView(APIView):
    permission_classes = [IsAuthenticated, IsFiscalizador]

    def get(self, request, vehiculo_id):
        fiscalizaciones = Fiscalizacion.objects.filter(
            vehiculo_id=vehiculo_id
        ).order_by("-fecha")

        data = [{
            "id": f.id,
            "fecha": f.fecha,
            "observacion": f.observacion,
            "fiscalizador": {
                "rut": f.fiscalizador.rut if f.fiscalizador else None,
                "nombre": f.fiscalizador.nombre if f.fiscalizador else None
            }
        } for f in fiscalizaciones]

        return Response(data)

#ER PDF DEL DOCUMENTO
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
