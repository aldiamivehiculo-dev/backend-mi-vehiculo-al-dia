from rest_framework import serializers
from .models import Usuario

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id','username','email','rut','fecha_nacimiento','telefono','password']
        extra_kwargs = {'password':{'write_only': True}}#hace que no se peda leer la contrasaeña cuando la api manda respuesta

    def create(self, validated_data):
        user = Usuario(
            username=validated_data['username'],
            email=validated_data['email'],
            rut=validated_data['rut'],
            fecha_nacimiento=validated_data.get('fecha_nacimiento'),
            residencia=validated_data.get('residencia'),
            telefono=validated_data.get('telefono')

        )
        user.set_password(validated_data['password']) #encripta la contraseña
        user.save()
        return user