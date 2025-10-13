from django.db import models
from django.conf import settings
#from django.contrib.auth.models import User
# Create your models here.

#Base de datos interna de vehiculos (autocompletados)
class VehiculoData(models.Model):
    patente = models.CharField(max_length=10, unique=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    año = models.PositiveIntegerField()
    color = models.CharField(max_length=30, blank=True, null=True)
    
    def __str__(self):
        return f"{self.patente} - {self.marca} {self.modelo}"

#Vehiculo registrado por el usuario
class Vehiculo(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vehiculos')
    patente = models.CharField(max_length=10, unique=True)
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    año = models.PositiveIntegerField()
    color = models.CharField(max_length=30, blank=True, null=True)
    alias = models.CharField(max_length=30, blank=True, null=True)