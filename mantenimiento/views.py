from rest_framework import generics, permissions
from .models import MantenimientoVehiculo
from .serializers import MantenimientoSerializer
from notificaciones.utils import crear_notificacion
# Create your views here. 

# Registrar un nuevo mantenimiento
class RegistrarMantenimientoView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MantenimientoSerializer

    def perform_create(self, serializer):
        #Se guarda el mantenimiento con el usuario autenticado
        mantenimiento = serializer.save(user=self.request.user)
        vehiculo = mantenimiento.vehiculo

        #Título notificación
        titulo = "Mantenimiento registrado"
        mensaje = (
            f"Se registró un mantenimiento para el vehículo {vehiculo.patente}. "
            f"Kilometraje: {mantenimiento.kilometraje} km. "
            f"Costo: ${mantenimiento.costo}."
        )

        #Meta para el frontend
        meta = {
            "mantenimiento_id": mantenimiento.id,
            "vehiculo_id": vehiculo.id,
            "vehiculo_patente": vehiculo.patente,
            "kilometraje": mantenimiento.kilometraje,
            "costo": str(mantenimiento.costo),
            "fecha": str(mantenimiento.fecha),
        }

        #Crear la notificación
        crear_notificacion(
            user=self.request.user,
            titulo=titulo,
            mensaje=mensaje,
            tipo="mantenimiento",
            meta=meta,
            send_email=False,
        )

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
