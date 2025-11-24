from django.shortcuts import render
from rest_framework import generics, permissions
from .models import Vehiculo, VehiculoData
from .serializers import VehiculoSerializer, VehiculoListSerializer, VehiculoUpdateSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

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

class VerificarPatenteView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        patente = request.query_params.get("patente", "").upper()

        if not patente:
            return Response({"error": "Debes enviar una patente"}, status=400)

        # Si ya existe en Vehiculo (registrado por un usuario)
        if Vehiculo.objects.filter(patente=patente).exists():
            return Response({
                "status": "registrado",
                "message": "Esta patente ya está registrada por un usuario."
            }, status=200)

        # Si existe en la base VehiculoData (autocompletar)
        try:
            vd = VehiculoData.objects.get(patente=patente)
            return Response({
                "status": "data",
                "marca": vd.marca,
                "modelo": vd.modelo,
                "anio": vd.año,
                "color": vd.color,
                "tipo": vd.tipo,
            }, status=200)
        except VehiculoData.DoesNotExist:
            return Response({
                "status": "nuevo",
                "message": "Patente no encontrada. Ingresa los datos manualmente."
            }, status=200)