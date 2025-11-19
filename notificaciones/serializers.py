from rest_framework import serializers
from .models import Notificacion

class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = [
            "id",
            "user",
            "titulo",
            "mensaje",
            "tipo",
            "leida",
            "creada_en",
            "leida_en",
            "enviada_email",
            "meta",
        ]
        read_only_fields = ["user", "creada_en", "leida_en", "enviada_email"]
