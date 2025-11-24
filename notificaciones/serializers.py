from rest_framework import serializers
from .models import Notificacion

# Serializer que transforma el modelo Notificacion en JSON para el frontend
class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion

        # Campos que se enviarán al frontend
        fields = [
            "id",             #ID de la notificación
            "user",           #Usuario dueño (se oculta en POST)
            "titulo",         #Título visible
            "mensaje",        #Descripción
            "tipo",           #ipo: documento, mantenimiento, qr, sistema
            "leida",          #Si el usuario la leyó
            "creada_en",      #Fecha de creación
            "leida_en",       #Cuándo la leyó
            "enviada_email",  #Si ya se envió por correo
            "meta",           #Información extra (vehículo_id, doc_id, qr_token)
        ]

        #Campos que no se permiten modificar manualmente
        read_only_fields = [
            "user",           #El backend asigna automáticamente al usuario logeado
            "creada_en",      #Se autogenera
            "leida_en",       #Se completa solo cuando el usuario abre la notificación
            "enviada_email",  #Se marca internamente cuando se envía correo
        ]

    #Guarda el usuario automáticamente desde el request
    def create(self, validated_data):
        """
        Crea una notificación asignando automáticamente el usuario
        que está realizando la petición.
        """
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
