from django.shortcuts import render
from rest_framework import generics, status, permissions
from .models import Usuario
from .serializer import UsuarioSerializer
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions
# Create your views here.

class RegistroUsuarioView(generics.CreateAPIView):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

#Rrcuperar contraseña usuario
Usuario = get_user_model()
class RecuperarContrasenaView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        try:
            user = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            return Response({"Error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        
        token = PasswordResetTokenGenerator().make_token(user)
        reset_link = f"http://localhost:3000/reset-password/{user.pk}/{token}"# frontend handlea el cambio

        #enviar correo de restablecer contraseña  
        send_mail(
            'recuperar contraseña',
            f'Usa este link para cambiar tu contraseña: {reset_link}',
            'noreply@mi-vehiculo.com',
            [email],
            fail_silently=False
        )
        return Response({"mensaje": "Se ha enviado un email con intrucciones"}, status=status.HTTP_200_OK)

class CambiarContrasenaView(APIView):
    permission_classes= [permissions.AllowAny]#usuario no logeado

    def post(self, request, *args, **kwarfs):
        user_id= request.data.get('user_id')
        token = request.data.get('token')
        new_password = request.data.get('new password')

        try:
            user = Usuario.objects.get(pk=user_id)
        except Usuario.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        
        if not PasswordResetTokenGenerator().check_token(user, token):
            return Response({"error": "token invalido o expirado"}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()
        return Response({"mensaje": "Contraseña actualizada correctamente"}, status=status.HTTP_200_OK)