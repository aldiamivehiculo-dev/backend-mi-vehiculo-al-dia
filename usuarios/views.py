from django.shortcuts import render
from rest_framework import generics
from .models import Usuario
from .serializer import UsuarioSerializer
# Create your views here.
class RegistroUsuarioView(generics.CreateAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer