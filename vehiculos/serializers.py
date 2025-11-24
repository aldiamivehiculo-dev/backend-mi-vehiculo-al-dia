from rest_framework import serializers
from .models import Vehiculo, VehiculoData

class VehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehiculo
        fields = ['id', 'patente', 'marca', 'modelo', 'año', 'color', 'alias', 'tipo']
        extra_kwargs = {
            'marca': {'required': False},
            'modelo': {'required': False},
            'año': {'required': False},
            'color': {'required': False},
            'tipo': {'required': False},
        }

    def create(self, validated_data):
        patente = validated_data['patente']
        tipo = validated_data.get('tipo', 'auto')

        # 1) Verificar si la patente ya está registrada por otro usuario
        if Vehiculo.objects.filter(patente=patente).exists():
            raise serializers.ValidationError({
                "patente": "Esta patente ya está registrada por otro usuario."
            })

        # 2) Intentar autocompletar desde la BD interna VehiculoData
        try:
            vd = VehiculoData.objects.get(patente=patente)

        except VehiculoData.DoesNotExist:
            # Si no existe, se crea el registro en VehiculoData
            vd = VehiculoData.objects.create(
                patente=patente,
                marca=validated_data.get('marca', ''),
                modelo=validated_data.get('modelo', ''),
                año=validated_data.get('año', 0),
                color=validated_data.get('color', ''),
                tipo=tipo,
            )

        # 3) Autocompletar los datos en el vehículo del usuario
        validated_data['marca'] = vd.marca
        validated_data['modelo'] = vd.modelo
        validated_data['año'] = vd.año
        validated_data['color'] = vd.color
        validated_data['tipo'] = vd.tipo

        # 4) Asignar usuario dueño del vehículo
        validated_data['user'] = self.context['request'].user
        
        return super().create(validated_data)

class VehiculoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehiculo
        fields = ['id', 'alias', 'patente']

class VehiculoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehiculo
        fields = ['alias', 'color', 'tipo'] #campo editable
