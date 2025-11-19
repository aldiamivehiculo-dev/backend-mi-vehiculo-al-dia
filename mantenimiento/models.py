from django.db import models
from django.contrib.auth import get_user_model
from vehiculos.models import Vehiculo
# Create your models here.

TIPO_SERVICIO = [
    ("aceite", "Cambio de aceite"),
    ("frenos", "Frenos"),
    ("motor", "Motor"),
    ("electrico", "Eléctrico"),
    ("completo", "Servicio completo"),
]

User = get_user_model()

class MantenimientoVehiculo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE)
    descripcion = models.TextField()
    kilometraje = models.PositiveBigIntegerField()
    fecha = models.DateField()
    costo = models.DecimalField(max_digits=12, decimal_places=2)

    fecha_registro = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.vehiculo.patente}" - {self.descripcion[:20]}

