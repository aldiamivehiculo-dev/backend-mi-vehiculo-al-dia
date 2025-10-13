from rest_framework import serializers
from .models import Vehiculo, VehiculoData

class VehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehiculo
        fields = ['id','patente','marca','modelo','año','color','alias']
        extra_kwargs = {
            'marca': {'required': False},
            'modelo': {'required': False},
            'año': {'required': False},
            'color': {'required': False},
        }

    def create(self, validated_data):
        patente = validated_data['patente']

        # Verificar si la patente ya está registrada en Vehiculo por otro usuario
        if Vehiculo.objects.filter(patente=patente).exists():
            raise serializers.ValidationError({
                "patente": "Esta patente ya está registrada por otro usuario."
            })

        # Intentamos autocompletar desde VehiculoData
        try:
            vd = VehiculoData.objects.get(patente=patente)
            validated_data['marca'] = vd.marca
            validated_data['modelo'] = vd.modelo
            validated_data['año'] = vd.año
            validated_data['color'] = vd.color

        except VehiculoData.DoesNotExist:
            # Si la patente no existe, se crea en VehiculoData
            vd = VehiculoData.objects.create(
                patente=patente,
                marca=validated_data.get('marca', ''),
                modelo=validated_data.get('modelo', ''),
                año=validated_data.get('año', 0),
                color=validated_data.get('color', '')
            )
            # Autocompletamos los campos desde el nuevo registro
            validated_data['marca'] = vd.marca
            validated_data['modelo'] = vd.modelo
            validated_data['año'] = vd.año
            validated_data['color'] = vd.color

        # Asociamos el vehículo al usuario que hace la solicitud
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class VehiculoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehiculo
        fields = ['id', 'alias']

class VehiculoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehiculo
        fields = ['alias', 'color'] #campo editable