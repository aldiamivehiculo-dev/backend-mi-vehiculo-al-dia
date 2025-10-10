from rest_framework import serializers
from .models import Usuario
from datetime import timedelta
from django.utils import timezone

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id','nombre','email','rut','fecha_nacimiento','residencia','telefono','password']
        extra_kwargs = {'password':{'write_only': True}}#hace que no se pueda leer la contrasaeña cuando la api manda respuesta

    def create(self, validated_data):
        user = Usuario(
            nombre=validated_data['nombre'],
            email=validated_data['email'],
            rut=validated_data['rut'],
            fecha_nacimiento=validated_data.get('fecha_nacimiento'),
            residencia=validated_data.get('residencia'),
            telefono=validated_data.get('telefono')

        )
        user.set_password(validated_data['password']) #encripta la contraseña
        user.save()
        return user
    
class UsuarioPerfilSerializer(serializers.ModelSerializer):
    class Meta:
        model =Usuario
        fields = ['id','nombre','email','rut','fecha_nacimiento','residencia','telefono']
        read_only_fields = ['rut']
    
    def update(self, instance, validated_data):
        nueva_fecha = validated_data.get('fecha_nacimiento')
        if nueva_fecha and nueva_fecha != instance.fecha_nacimiento:
            if instance.update_at and timezone.now() - instance.update_at < timedelta(days=30):
                raise serializers.ValidationError(
                    
                    {"fecha_nacimiento": "Solo puedes cambiar tu fecha de nacimiento 1 vez cada 30 días."}
                
                )

        return super().update(instance, validated_data)