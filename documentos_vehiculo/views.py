from django.shortcuts import render
from django.http import FileResponse, Http404
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from .models import DocumentoVehicular
from .serializers import DocumentoVehicularSerializer
import os, mimetypes
from django.shortcuts import get_object_or_404, redirect
from vehiculos.models import Vehiculo
from rest_framework.response import Response
from notificaciones.utils import crear_notificacion
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import AccessToken
# Firebase
import firebase_admin
from firebase_admin import storage
from django.core.files.uploadedfile import InMemoryUploadedFile
import uuid


# ============================================================
# FUNCIÓN PARA SUBIR ARCHIVOS A FIREBASE STORAGE
# ============================================================
def subir_pdf_firebase(file):
    # MUY IMPORTANTE: reiniciar el puntero del archivo
    file.seek(0)

    ext = file.name.split('.')[-1]
    filename = f"documentos/{uuid.uuid4()}.{ext}"

    bucket = storage.bucket()
    blob = bucket.blob(filename)

    blob.upload_from_file(file, content_type=file.content_type)
    blob.make_public()

    return blob.public_url

# ============================================================
# CREAR DOCUMENTO
# ============================================================
class DocumentoCreateView(generics.CreateAPIView):
    serializer_class = DocumentoVehicularSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DocumentoVehicular.objects.filter(user=self.request.user)

    def perform_create(self, serializer):

        # 1) Guardamos documento + usuario (validado con OCR en serializer)
        doc = serializer.save(user=self.request.user)

        # 2) archivo recibido en la request
        archivo_subido = self.request.FILES.get("archivo")

        if archivo_subido:
            # 3) subir a firebase
            url = subir_pdf_firebase(archivo_subido)

            # 4) limpiar FileField y guardar URL
            doc.archivo = None
            doc.archivo_url = url
            doc.save()

        # ---------------------------------------------------
        # NOTIFICACIÓN
        # ---------------------------------------------------
        tipo_display = doc.get_tipo_display()
        titulo = f"Documento {tipo_display} subido"
        mensaje = (
            f"Se ha subido un documento de tipo {tipo_display} "
            f"para el vehículo {doc.vehiculo.patente}."
        )

        meta = {
            "documento_id": doc.id,
            "vehiculo_id": doc.vehiculo_id,
            "vehiculo_patente": doc.vehiculo.patente,
            "tipo": doc.tipo,
        }

        crear_notificacion(
            user=self.request.user,
            titulo=titulo,
            mensaje=mensaje,
            tipo="documento",
            meta=meta,
            send_email=False,
        )



# ============================================================
# LISTAR DOCUMENTOS
# ============================================================
class DocumentoListView(generics.ListAPIView):
    serializer_class = DocumentoVehicularSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = (
            DocumentoVehicular.objects
            .filter(user=self.request.user)
            .select_related('vehiculo')
            .order_by('-fecha_subida')
        )

        tipo = self.request.query_params.get('tipo')
        if tipo:
            qs = qs.filter(tipo=tipo)

        estado = self.request.query_params.get('estado')
        if estado == 'activo':
            qs = qs.filter(activo=True)
        elif estado == 'inactivo':
            qs = qs.filter(activo=False)

        vehiculo_id = self.request.query_params.get('vehiculo')
        if vehiculo_id:
            qs = qs.filter(vehiculo_id=vehiculo_id)

        caducados = self.request.query_params.get('caducados')
        if caducados == '1':
            hoy = timezone.now().date()
            qs = qs.filter(fecha_vencimiento__isnull=False, fecha_vencimiento__lt=hoy)

        return qs



# ============================================================
# DETALLE DOCUMENTO
# ============================================================
class DocumentoDetailView(generics.RetrieveAPIView):
    serializer_class = DocumentoVehicularSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            DocumentoVehicular.objects
            .filter(user=self.request.user)
            .select_related('vehiculo')
        )



# ============================================================
# ELIMINAR DOCUMENTO
# ============================================================
class DocumentoDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DocumentoVehicular.objects.filter(user=self.request.user)



# ============================================================
# DESCARGAR DOCUMENTO (LEGACY, YA NO SE USA CON FIREBASE)
# ============================================================
class DocumentoDownloadView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        token = request.query_params.get("token")

        # Validación del token (QR)
        if token:
            try:
                AccessToken(token)
            except Exception:
                return Response({"detail": "Token inválido"}, status=401)
        else:
            if not request.user.is_authenticated:
                return Response({"detail": "Authentication credentials were not provided."}, status=401)

        # Buscar documento
        try:
            doc = DocumentoVehicular.objects.get(pk=pk)
        except DocumentoVehicular.DoesNotExist:
            raise Http404("Documento no encontrado")

        # USAR archivo_url
        if not doc.archivo_url:
            raise Http404("El documento no tiene archivo asociado")

        #REDIRIGIR DIRECTAMENTE A FIREBASE
        return redirect(doc.archivo_url)
# ============================================================
# DOCUMENTOS ACTIVOS POR VEHÍCULO
# ============================================================
class DocumentoActivosPorVehiculoView(generics.ListAPIView):

    serializer_class = DocumentoVehicularSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        vehiculo_id = self.request.query_params.get("vehiculo")

        qs = (
            DocumentoVehicular.objects
            .filter(user=self.request.user, activo=True)
            .select_related("vehiculo")
        )
        
        if vehiculo_id:
            qs = qs.filter(vehiculo_id=vehiculo_id)
        
        return qs



# ============================================================
# HISTORIAL POR TIPO
# ============================================================
class DocumentoHistorialPorTipoView(generics.ListAPIView):
    serializer_class = DocumentoVehicularSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        tipo = self.request.query_params.get("tipo")
        vehiculo_id = self.request.query_params.get("vehiculo")

        if not tipo:
            return DocumentoVehicular.objects.none()

        qs = (
            DocumentoVehicular.objects
            .filter(user=self.request.user, tipo=tipo)
            .select_related("vehiculo")
            .order_by("-fecha_subida")
        )

        if vehiculo_id:
            qs = qs.filter(vehiculo_id=vehiculo_id)
            
        return qs



# ============================================================
# ESTADO DE DOCUMENTOS DEL VEHÍCULO
# ============================================================
class DocumentoEstadoVehiculoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, vehiculo_id):
        vehiculo = get_object_or_404(Vehiculo, pk=vehiculo_id, user=request.user)

        tipos_requeridos = ["pc","so", "rt"]
        hoy = timezone.now().date()

        documentos = DocumentoVehicular.objects.filter(
            vehiculo=vehiculo,
            user=request.user
        )

        faltantes = []
        vencidos = []
        data_docs = {}

        for tipo in tipos_requeridos:
            doc = documentos.filter(tipo=tipo, activo=True).order_by("-fecha_vencimiento").first()

            if not doc:
                faltantes.append(tipo)
                data_docs[tipo] = None
                continue

            data_docs[tipo] = {
                "id": doc.id,
                "fecha_vencimiento": doc.fecha_vencimiento,
                "activo": doc.activo
            }

            if doc.fecha_vencimiento and doc.fecha_vencimiento < hoy:
                vencidos.append(tipo)

        al_dia = (len(faltantes) == 0 and len(vencidos) == 0)

        return Response({
            "vehiculo": vehiculo.id,
            "patente": vehiculo.patente,
            "al_dia": al_dia,
            "faltantes": faltantes,
            "vencidos": vencidos,
            "documentos": data_docs
        }, status=status.HTTP_200_OK)
