from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
User = get_user_model()

class Notificacion(models.Model):
    TIPOS = [
        ("documento", "Documento por vencer / subido"),
        ("mantenimiento", "Mantenimiento registrado"),
        ("qr", "QR generado / vencido"),
        ("sistema", "Notificación del sistema"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notificaciones"
    )
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPOS, default="sistema")

    leida = models.BooleanField(default=False)
    creada_en = models.DateTimeField(auto_now_add=True)
    leida_en = models.DateTimeField(null=True, blank=True)

    enviada_email = models.BooleanField(default=False)

    # Datos extra: id de vehículo, documento, qr, etc.
    meta = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-creada_en"]

    def __str__(self):
        return f"[{self.get_tipo_display()}] {self.titulo[:40]}"

