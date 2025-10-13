from django.shortcuts import render
from rest_framework import generics, permissions
from .models import Vehiculo
from .serializers import VehiculoSerializer, VehiculoListSerializer, VehiculoUpdateSerializer

# Create your views here.

#Crear vehiculo
class VehiculoCreateView(generics.CreateAPIView):
    queryset = Vehiculo.objects.all()
    serializer_class = VehiculoSerializer
    permission_classes = [permissions.IsAuthenticated]

#Lista de los vehiculos
class VehiculoListView(generics.ListAPIView):
    serializer_class = VehiculoListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Vehiculo.objects.filter(user=self.request.user)
class VehiculoDetailView(generics.RetrieveAPIView):

    serializer_class = VehiculoSerializer
    permission_classes =[permissions.IsAuthenticated]
    queryset = Vehiculo.objects.all()

#actualizar vehiculo
class VehiculoUpdateView(generics.UpdateAPIView):
    serializer_class = VehiculoUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Vehiculo.objects.filter(user=self.request.user)

class VehiculoDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Solo el usuario dueño puede eliminar
        return Vehiculo.objects.filter(user=self.request.user)
