from django.shortcuts import render
from django.http import FileResponse, Http404
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from .models import DocumentoVehicular
from .serializers import DocumentoVehicularSerializer
import os, mimetypes
from django.shortcuts import get_object_or_404
from vehiculos.models import Vehiculo
from rest_framework.response import Response
from notificaciones.utils import crear_notificacion
from notificaciones.models import Notificacion


# Create your views here.

class DocumentoCreateView(generics.CreateAPIView):
    serializer_class = DocumentoVehicularSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DocumentoVehicular.objects.filter(user=self.request.user)
    
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

class DocumentoDetailView(generics.RetrieveAPIView):
    serializer_class = DocumentoVehicularSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            DocumentoVehicular.objects
            .filter(user=self.request.user)
            .select_related('vehiculo')
        )

class DocumentoDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DocumentoVehicular.objects.filter(user=self.request.user)

class DocumentoDownloadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            doc = DocumentoVehicular.objects.get(pk=pk, user=request.user)
        except DocumentoVehicular.DoesNotExist:
            raise Http404("Documento no encontrado")

        if not doc.archivo:
            raise Http404("El documento no tiene archivo asociado")
        
        filename = os.path.basename(doc.archivo.name)
        content_type, _ = mimetypes.guess_type(filename)

        return FileResponse(
            doc.archivo.open('rb'),
            as_attachment=True,
            filename=filename,
            content_type=content_type or 'application/octet-stream'

        )

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
            qs=qs.filter(vehiculo_id=vehiculo_id)
            
        return qs

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

            #guardar info
            data_docs[tipo] ={
                "id": doc.id,
                "fecha_vencimiento": doc.fecha_vencimiento,
                "activo": doc.activo
            }

            #vencidos
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

