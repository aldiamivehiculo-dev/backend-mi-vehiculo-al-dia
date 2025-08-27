from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your mode

#definimos la clase usuario de la app Usuarios
class Usuario(AbstractUser):
    rut = models.CharField(max_length=12, unique=True) #identificador chileno
    fecha_nacimiento = models.DateField(null=True , blank=True)#fecha de nacimineto del usuario
    residencia = models.CharField(max_length=255, blank=True)#donde vive el usuario
    telefono = models.CharField(max_length=11, blank=True)#telefono 
    created_at = models.DateTimeField(auto_now_add=True)#fecha ceacion de cuenta
    update_at = models.DateTimeField(auto_now=True)#fecha actualizacion de fecha

    def __str__(self):
        return f"{self.username}({self.rut})"# que el usuario muestre nombre legible
