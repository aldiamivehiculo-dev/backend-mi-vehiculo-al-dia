from rest_framework import serializers
from vehiculos.models import Vehiculo
from documentos_vehiculo.models import DocumentoVehicular
from .models import Fiscalizacion
from django.utils import timezone

TIPOS = ["pc", "so", "rt"]

class VehiculoFiscalizadorSerializer(serializers.ModelSerializer):
    documentos = serializers.SerializerMethodField()
    advertencias = serializers.SerializerMethodField()
    dueño = serializers.SerializerMethodField()

    class Meta:
        model = Vehiculo
        fields = [
            "id",
            "patente",
            "marca",
            "modelo",
            "año",
            "color",
            "alias",
            "tipo",
            "dueño",
            "documentos",
            "advertencias"
        ]

    def get_dueño(self, obj):
        return {
            "rut": obj.user.rut,
            "nombre": obj.user.nombre
        }

    def get_documentos(self, obj):#lo que le muestra al fiscalizaro
        tipos = ["pc", "so", "rt"]
        resultado = {}

        for tipo in TIPOS:
            doc = (DocumentoVehicular.objects.filter(vehiculo=obj, tipo=tipo).order_by("-fecha_subida").first())
            if not doc:
                resultado[tipo] = None
            else:
                resultado[tipo] = {
                    "id": doc.id,
                    "tipo": doc.tipo,
                    "fecha_subida": doc.fecha_subida,
                    "fecha_vencimiento": doc.fecha_vencimiento,
                    "activo": doc.activo,
                    "puntaje_validacion": doc.puntaje_validacion,
                    "detalles_validacion": doc.detalles_validacion,
                }

        return resultado
    
    def get_advertencias(self, obj):
        advertencias = []
        hoy = timezone.now().date()

        for tipo in TIPOS:
            doc = (DocumentoVehicular.objects.filter(vehiculo=obj, tipo=tipo, activo=True).order_by("-fecha_subida").first())
            # Falta documento
            if not doc:
                advertencias.append(f"Falta documento: {tipo.upper()}")
                continue
            # Documento vencido
            if doc.fecha_vencimiento and doc.fecha_vencimiento < hoy:
                advertencias.append(f"Documento vencido: {tipo.upper()}")
            # Puntaje bajo           
            if doc.puntaje_validacion < 85:
                advertencias.append(f"Puntaje bajo ({doc.puntaje_validacion}) en {tipo.upper()}")
            # Validaciones OCR fallidas            
            for key, val in doc.detalles_validacion.items():
                if val is False:
                    advertencias.append(f"Validación fallida en {tipo.upper()}: {key}")
        return advertencias
            
class FiscalizacionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Fiscalizacion
        fields = ["id", "vehiculo", "token", "advertencias", "fecha"]

        read_only_fields = ["id", "fecha"]

    def create(self, validated_data):
        # El fiscalizador viene desde la vista
        fiscalizador = self.context["request"].user
        validated_data["fiscalizador"] = fiscalizador
        return super().create(validated_data)
