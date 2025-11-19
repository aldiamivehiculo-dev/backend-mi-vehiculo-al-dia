from django.db import models
from django.conf import settings
from vehiculos.models import Vehiculo

# Create your models here.

class Fiscalizacion(models.Model):
    fiscalizador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="fiscalizaciones_realizadas")
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, related_name="fiscalizaciones")
    fecha = models.DateTimeField(auto_now_add=True)
    observacion = models.TextField(blank=True, null=True)


    def __str__(self):
        return f"Fiscalizacion{self.id} de {self.vehiculo.patente}"
    
    #latitud = models.FloatField(null=True, blank=True)
    #longitud = models.FloatField(null=True, blank=True)