from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.shortcuts import get_object_or_404
from datetime import timedelta
import qrcode
import base64
from io import BytesIO
from .models import SharedAccess, SharedAccessLog
from .serializers import SharedAccessSerializer, SharedAccessLogSerializer
from vehiculos.models import Vehiculo
from documentos_vehiculo.models import DocumentoVehicular
from django.contrib.auth import get_user_model
from django.http import FileResponse, Http404

# Create your views here.

class GenerateShareQR(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        vehiculo_id = request.data.get("vehiculo_id")
        hours = request.data.get("hours", 1)
        is_prestamo = str(request.data.get("is_prestamo", False)).lower() == "true"
        receptor_nombre = request.data.get("receptor_nombre")
        receptor_rut = request.data.get("receptor_rut")

        #validar horas

        try:
            hours = int(hours)
        except:
            return Response({"error": "hours debe ser numérico"}, status=status.HTTP_400_BAD_REQUEST)
        
        #OBTENER VEHICULO
        vehiculo = get_object_or_404(Vehiculo, id=vehiculo_id)

        # veridicar que el usuario sea dueño
        if vehiculo.user != request.user:
            return Response({"error": "No tienes permiso para generar QR de este vehículo"},status=status.HTTP_403_FORBIDDEN)
        
        #SI ES PRETAMO receptor obligado
        if is_prestamo:
            if not receptor_nombre or not receptor_rut:
                return Response({"error": "Para préstamos, receptor_nombre y receptor_rut son obligatorios"}, status=status.HTTP_400_BAD_REQUEST)
            
            #validar que el RUT pertenezca a un usuario existente
            User = get_user_model()
            
            try:
                U_dest = User.objects.get(rut=receptor_rut)
            
            except User.DoesNotExist:
                return Response({"error": "El RUT del receptor no corresponde a un usuario registrado."}, status=status.HTTP_400_BAD_REQUEST)
            
            # si no envían nombre, lo tomamos del usuario
            if not receptor_nombre:
                receptor_nombre = getattr(U_dest, "nombre", None)
        else:
            receptor_nombre = None
            receptor_rut = None
        #Ccalcular eexpiracion
        expires_at = timezone.now() + timedelta(hours=hours)

        #crear registro
        shared = SharedAccess.objects.create(
            user=request.user,
            vehiculo=vehiculo,
            expires_at=expires_at,
            is_prestamo=is_prestamo,
            receptor_nombre=receptor_nombre,
            receptor_rut=receptor_rut
        )

        #construir url publica
        share_url = request.build_absolute_uri(f"/api/accesos/info/{shared.token}/")

        #generr qr 
        qr = qrcode.make(share_url)
        buf = BytesIO()
        qr.save(buf, format="PNG")
        qr_base64 = base64.b64encode(buf.getvalue()).decode()

        return Response({
            "id": str(shared.id),
            "token": shared.token,
            "expires_at": shared.expires_at,
            "share_url": share_url,
            "qr_base64": qr_base64,
            "is_prestamo": shared.is_prestamo,
            "receptor_nombre": shared.receptor_nombre,
            "receptor_rut": shared.receptor_rut
            }, status=status.HTTP_201_CREATED)
    
class SharedAccessInfoView(APIView):
    #endpoint publico que retorna la info ligada a un token de acceso

    authentication_classes = [] #publico
    permission_classes = [] #sin auth

    def get(self, request, token):
        #buscar token
        shared = get_object_or_404(SharedAccess, token=token)

        #validar expiracion
        if shared.is_revoked:
            return Response({"valid": False, "message": "Acceso revocado"}, status=status.HTTP_403_FORBIDDEN)
        
        if timezone.now()> shared.expires_at:
            return Response({"valid": False, "message": "Aceceso expirado"}, status=status.HTTP_403_FORBIDDEN)
        
        #obtener vehiculo asociadp
        vehiculo = shared.vehiculo
        
        #buscar documentos activos del vehiculo
        docs = DocumentoVehicular.objects.filter(
            vehiculo=vehiculo,
            activo=True
        ).order_by("-fecha_subida")

        documentos = {}
        for t in ["pc", "so", "rt"]:
            doc = docs.filter(tipo=t).first()
            if doc:

                if request.user.is_authenticated:
                    archivo = request.build_absolute_uri(doc.archivo.url)
                else:
                    archivo = None
                
                documentos[t] = {
                    "id": doc.id,
                    "tipo": t,
                    "fecha_vencimiento":doc.fecha_vencimiento,
                    "archivo": archivo
                }
            else:
                documentos[t] = None
        
        #registrar acceso al log
        SharedAccessLog.objects.create(
            shared=shared,
            usuario=request.user if request.user.is_authenticated else None,
            ip=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            is_prestamo=shared.is_prestamo,
        )

        #RESPUESTA
        data = {
            "valid":True,
            "vehiculo": {
                "patente": vehiculo.patente,
                "marca": vehiculo.marca,
                "modelo": vehiculo.modelo,
                "color": vehiculo.color,
            },
            "documentos" : documentos
        }

        if shared.is_prestamo:
            data["prestamo"] ={
                "receptor_nombre": shared.receptor_nombre,
                "receptor_rut": shared.receptor_rut
            }
        return Response(data)

class RevokeSharedAccessView(APIView):
    """permite al usuario revocar el acceso al qr compartido"""

    permission_classes =[IsAuthenticated]

    def patch(self, request, uuid):
        shared = get_object_or_404(SharedAccess, id=uuid)

        #validar que el solicitante sea el creador
        if shared.user != request.user:
            return Response({"detail": "No autorizado para revocar este acceso."}, status=status.HTTP_403_FORBIDDEN)
        
        #YA ESTA REVOCADO
        if shared.is_revoked:
            return Response({"detail": "Este acceso ya está revocado."}, status=status.HTTP_200_OK)
        
        try: #marcar como revocado
            shared.is_revoked = True
            shared.save()
        except Exception as e:
            #fallo de acrualizacion en la baese de datos
            return Response({"detail": "Error al revocar acceso.", "error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"detail": "Acceso revocado exitosamente."}, status=status.HTTP_200_OK)

class SharedAccessListView(APIView):
     """lista de todos los acceso compartidos"""
     permission_classes = [IsAuthenticated]
     
     def get(self, request):
        shared = SharedAccess.objects.filter(user=request.user).order_by("-created_at")
        serializer = SharedAccessSerializer(shared, many=True)
        return Response(serializer.data)

class SharedAccessLogsView(APIView):
    """lista los accesos realizados aun tokenN"""

    permission_classes =[IsAuthenticated]
    
    def get(self, request, uuid):
        shared = get_object_or_404(SharedAccess, id=uuid)

        #solo el dueño puede ver el log
        if shared.user != request.user:
            return Response({"detail": "No autorizado"}, status=status.HTTP_403_FORBIDDEN)
        
        logs = shared.access_logs.all()
        ser = SharedAccessLogSerializer(logs, many=True)
        return Response(ser.data)

class DownloadSharedDocumentView(APIView):
    """
    Descarga/visualiza un PDF a través de un token compartido.
    Requisitos:
    - token válido
    - no revocado
    - no expirado
    - doc pertenece al mismo vehículo del token
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request, token, doc_id):
        shared = get_object_or_404(SharedAccess, token=token)

        if shared.is_revoked:
            return Response({"detail": "Acceso revocado"}, status=status.HTTP_403_FORBIDDEN)
        if timezone.now() > shared.expires_at:
            return Response({"detail": "Acceso expirado"}, status=status.HTTP_403_FORBIDDEN)

        # documento debe ser ACTIVO y del mismo vehículo
        doc = get_object_or_404(
            DocumentoVehicular,
            id=doc_id,
            vehiculo=shared.vehiculo,
            activo=True,
        )

        if not doc.archivo:
            raise Http404("Documento sin archivo")

        # Log de acceso 
        SharedAccessLog.objects.create(
            shared=shared,
            usuario=request.user if request.user.is_authenticated else None,
            ip=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT'),
            is_prestamo=shared.is_prestamo, 
        )

        return FileResponse(doc.archivo.open('rb'), content_type='application/pdf')

        

