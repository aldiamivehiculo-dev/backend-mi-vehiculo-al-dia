from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from .models import Usuario
from datetime import timedelta
from django.utils import timezone
import re

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'nombre', 'email', 'rut', 'fecha_nacimiento', 'residencia', 'telefono', 'password', 'rol']
        extra_kwargs = {'password': {'write_only': True}}

    # --- 1. NORMALIZACIÓN (to_internal_value) ---
    # Limpia el formato de entrada (quita puntos, guiones) y lo convierte al estándar XXXXXXX-Y
    def to_internal_value(self, data):
        internal_value = super().to_internal_value(data)

        if 'rut' in internal_value and internal_value['rut']:
            rut = str(internal_value['rut']).upper()
            
            # 1. Eliminar todos los caracteres que no sean dígitos o 'K'
            rut_limpio = re.sub(r'[^0-9K]', '', rut)

            # 2. Re-formatear al estándar "cuerpo-dv" para la validación
            if len(rut_limpio) >= 2:
                cuerpo = rut_limpio[:-1] # Toda la parte numérica
                dv = rut_limpio[-1]      # El último caracter es el dígito verificador
                internal_value['rut'] = f"{cuerpo}-{dv}"
            else:
                # Si es muy corto, se deja limpio para que la validación lo rechace
                internal_value['rut'] = rut_limpio

        return internal_value

    # --- 2. VALIDACIÓN (validate_rut) ---
    def validate_rut(self, value):
        if not value:
            raise serializers.ValidationError("El campo RUT no puede estar vacío.")

        # VALIDACIÓN A: Formato y Largo (6 a 8 dígitos en el cuerpo)
        # Esto SÍ se mantiene para asegurar la estructura XXXXXXX-Y.
        if not re.match(r'^\d{6,8}-[\dK]$', value):
            raise serializers.ValidationError("Formato de RUT inválido. Ejemplo válido: 12345678-9 (o 9876543-K)")
        # VALIDACIÓN C: Unicidad (Comprobar si ya existe)
        # Esto es lo que usará el sistema para distinguir a los usuarios:
        # "21546556-9" es diferente de "21546556-8".
        if Usuario.objects.filter(rut=value).exists():
            raise serializers.ValidationError("Ya existe un usuario con este RUT registrado.")

        return value
    # --- Validación del Rol ---
    def validate_rol(self, value):
        request = self.context.get('request')

        # Solo admins pueden asignar fiscalizador o admin
        if value in ['fiscalizador', 'admin']:
            if not request or not request.user.is_authenticated:
                raise serializers.ValidationError("Debe estar autenticado para asignar roles especiales.")
            if not (request.user.is_staff or request.user.is_superuser):
                raise serializers.ValidationError("Solo el administrador puede crear usuarios con este rol.")

        return value

    # --- Creación del usuario ---
    def create(self, validated_data):
        user = Usuario(
            nombre=validated_data['nombre'],
            email=validated_data['email'],
            rut=validated_data['rut'],
            fecha_nacimiento=validated_data.get('fecha_nacimiento'),
            residencia=validated_data.get('residencia'),
            telefono=validated_data.get('telefono'),
            rol=validated_data.get('rol', 'usuario')  # Por defecto: usuario
        )
        user.set_password(validated_data['password'])  # Encripta la contraseña
        user.save()
        return user
    
class UsuarioPerfilSerializer(serializers.ModelSerializer):

    class Meta:
        model =Usuario
        fields = ['id','nombre','email','rut','fecha_nacimiento','residencia','telefono']
        read_only_fields = ['rut', 'email']#arreglar
    
    def update(self, instance, validated_data):
        nueva_fecha = validated_data.get('fecha_nacimiento')
        if nueva_fecha and nueva_fecha != instance.fecha_nacimiento:

            ultimo_cambio = instance.fecha_nacimiento_ultima_actualizacion
            
            if ultimo_cambio and timezone.now() - ultimo_cambio < timedelta(days=30):
                raise serializers.ValidationError(
                    
                    {"fecha_nacimiento": "Solo puedes cambiar tu fecha de nacimiento 1 vez cada 30 días."}
                
                )

        return super().update(instance, validated_data)

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        if not user.is_active:
            raise serializers.ValidationError("Esta cuenta ha sido desactivada.")
        return data
