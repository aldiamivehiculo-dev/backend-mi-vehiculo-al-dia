from django.db import models
from django.conf import settings
from vehiculos.models import Vehiculo

# Create your models here.

class Fiscalizacion(models.Model):
    fiscalizador = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,null=True,related_name="fiscalizaciones_realizadas"                                 )
    vehiculo = models.ForeignKey(Vehiculo,on_delete=models.CASCADE,related_name="fiscalizaciones")
    token = models.CharField(max_length=200, null=True, blank=True)  # TOKEN QR ESCANEADO
    advertencias = models.JSONField(default=list)  # LISTA DE ADVERTENCIAS
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Fiscalización {self.id} - {self.vehiculo.patente}"
