from rest_framework import serializers
from .models import SharedAccess, SharedAccessLog

class SharedAccessSerializer(serializers.ModelSerializer):
    is_valid = serializers.SerializerMethodField()

    vehiculo_patente = serializers.CharField(source="vehiculo.patente", read_only=True)
    qr_base64 = serializers.CharField(read_only=True)


    class Meta:
        model = SharedAccess
        fields = [
            "id",
            "token",
            "vehiculo_patente",
            "created_at",
            "expires_at",
            "is_revoked",
            "is_valid",
            "is_prestamo",
            "receptor_nombre",
            "receptor_rut",
            "qr_base64",

        ]

    def get_is_valid(self, obj):
        return obj.is_valid
       
class SharedAccessLogSerializer(serializers.ModelSerializer):
    usuario_rut = serializers.CharField(source="usuario.rut", read_only=True)

    class Meta:
        model = SharedAccessLog
        fields =[
            "accessed_at",
            "ip",
            "user_agent",
            "usuario_rut",
            "is_prestamo",
        ]