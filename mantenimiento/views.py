from rest_framework import generics, permissions
from .models import MantenimientoVehiculo
from .serializers import MantenimientoSerializer

# Create your views here.

# Registrar un nuevo mantenimiento
class RegistrarMantenimientoView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MantenimientoSerializer
# Listar mantenimientos por vehículo
class ListarMantenimientosView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MantenimientoSerializer
    
    def get_queryset(self):
        # Filtrar mantenimientos del usuario por vehículo
        vehiculo_id = self.request.query_params.get("vehiculo")
        return MantenimientoVehiculo.objects.filter(user=self.request.user,vehiculo_id=vehiculo_id).order_by("-fecha")
# Actualizar un mantenimiento existente    
class ActualizarMantenimientoView(generics.UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MantenimientoSerializer

    def get_queryset(self):
        # Solo permite modificar mantenimientos del usuario
        return MantenimientoVehiculo.objects.filter(user=self.request.user)    
# Eliminar un mantenimiento
class EliminarMantenimientoView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Solo permite borrar mantenimientos propios
        return MantenimientoVehiculo.objects.filter(user=self.request.user)
