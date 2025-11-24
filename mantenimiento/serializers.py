from rest_framework import serializers
from .models import MantenimientoVehiculo

class MantenimientoSerializer(serializers.ModelSerializer):
    vehiculo_patente = serializers.CharField(source="vehiculo.patente", read_only=True)

    class Meta:
        model = MantenimientoVehiculo
        fields =[
            "id",
            "vehiculo",
            "vehiculo_patente",
            "descripcion",
            "kilometraje",
            "fecha",
            "costo",
            "fecha_registro",

        ]
        read_only_fields=["user"]
    
    def create(self, validated_data):
        validated_data["user"]= self.context["request"].user
        return super().create(validated_data)

