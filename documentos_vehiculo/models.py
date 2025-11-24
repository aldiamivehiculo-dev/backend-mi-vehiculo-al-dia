from django.db import models
from django.conf import settings
from vehiculos.models import Vehiculo

# Create your models here.
class DocumentoVehicular(models.Model):
    #tipos de documentos permitidos
    TIPOS =[
        ('rt', 'Revision técnica'),
        ('pc', 'Permiso de circulación'),
        ('so', 'Soap')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, related_name='documentos')
    tipo = models.CharField(max_length=2, choices=TIPOS)
    archivo = models.FileField(upload_to='documentos/', null=True, blank=True)
    archivo_url = models.URLField(max_length=500, null=True, blank=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=True)
    puntaje_validacion = models.PositiveIntegerField(default=0)
    detalles_validacion = models.JSONField(default=dict)


    class Meta:
        indexes = [
            models.Index(fields=['user', 'vehiculo','tipo','activo'])
        ]

    def __str__(self):
        estado = "Activo" if self.activo else "Inactivo"
        return f"{self.vehiculo.patente} - {self.get_tipo_display()} ({estado})"
