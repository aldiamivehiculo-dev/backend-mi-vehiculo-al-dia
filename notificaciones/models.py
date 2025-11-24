from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


#almacena cualquier notificación que recibe el usuario
class Notificacion(models.Model):
    #Tipos de notificación disponibles
    TIPOS = [
        ("documento", "Documento por vencer / subido"),   #Documentos PC/SO/RT
        ("mantenimiento", "Mantenimiento registrado"),    #Registros de mantención
        ("qr", "QR generado / vencido"),                  #Accesos compartidos y fiscalización
        ("sistema", "Notificación del sistema"),          #Notificaciones generales
    ]

    #Usuario dueño de la notificación
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notificaciones"
    )

    titulo = models.CharField(max_length=200)   #Título visible para el usuario
    mensaje = models.TextField()                #Descripción de la notificación

    #Tipo de notificación para clasificarla
    tipo = models.CharField(
        max_length=20,
        choices=TIPOS,
        default="sistema"
    )

    #Estado de lectura
    leida = models.BooleanField(default=False)          #Si el usuario abrió la notificación
    creada_en = models.DateTimeField(auto_now_add=True) #Fecha de creación
    leida_en = models.DateTimeField(null=True, blank=True) #Fecha en que se marcó como leída

    enviada_email = models.BooleanField(default=False)  #Siya se envió por correo

    #Información adicional como: vehículo_id, documento_id, fecha_vencimiento, token_qr, etc.
    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-creada_en"]  #Notificaciones más recientes primero

    def __str__(self):
        #Representación legible de la notificación
        return f"[{self.get_tipo_display()}] {self.titulo[:40]}"
