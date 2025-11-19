from django.db import models
import uuid
from django.conf import settings
from django.utils import timezone
from vehiculos.models import Vehiculo
# Create your models here.

class SharedAccess(models.Model):

    #id del registro
    """
    Representa un enlace/QR compartido para los documentos
    de un vehículo. Sirve tanto para fiscalización como para
    casos donde el dueño presta el vehículo.
    
    """
    id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="shared_links") #usuario que genero el qr
    vehiculo = models.ForeignKey(Vehiculo,on_delete=models.CASCADE,related_name="shared_links")#vehiulo asoiado a token
    token = models.CharField(max_length=64,unique=True,db_index=True)#token unico

    #¿Es un acceso originado por préstamo?
    # False → Fiscalización normal
    # True → Usuario prestado temporal
    is_prestamo = models.BooleanField(default=False)
    receptor_nombre=models.CharField(max_length=255, blank=True, null=True)
    receptor_rut = models.CharField(max_length=20, blank=True, null=True)

    #control de expiracion
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(db_index=True)

    #contrl de revocacion manual
    is_revoked = models.BooleanField(
        default=False,
        db_index=True
    )

    def save(self, *args, **kwargs):
        #si no hay token
        if not self.token:
            self.token = uuid.uuid4().hex
        super().save(*args, **kwargs)
    

    @property
    def is_valid(self):
        #avisa si el qr esta expirado o no
        return(not self.is_revoked) and (timezone.now() < self.expires_at)
    
    def __str__(self):
        t = "PRESTAMO" if self.is_prestamo else "FISC"
        return f"{self.vehiculo.patente} [{t}] {self.token[:8]}..."

class SharedAccessLog(models.Model):
    shared = models.ForeignKey(SharedAccess,on_delete=models.CASCADE,related_name="access_logs")
    accessed_at = models.DateTimeField(auto_now_add=True)
    ip = models.GenericIPAddressField(null=True, blank=True)  #ip desde donde accede el cliente
    user_agent = models.TextField(null=True, blank=True) #informacion del navegador
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)#si el usuaio esta autenticado identificamos quien acedio
    is_prestamo = models.BooleanField(default=False)
    class Meta:
        ordering = ["-accessed_at"]
    
    def __str__(self):
        u = self.usuario.rut if self.usuario else "anon"
        return f"{self.shared.token[:8]} - {u} @ {self.accessed_at}"