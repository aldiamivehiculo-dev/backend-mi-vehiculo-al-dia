from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import UsuarioSerializer, UsuarioPerfilSerializer
from django.utils import timezone
from datetime import timedelta

# Obtener el modelo de usuario actual
Usuario = get_user_model()

# CREAR USUARIO
class RegistroUsuarioView(generics.CreateAPIView):
    """
    API para registrar un nuevo usuario.
    """
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

# RECUPERAR CONTRASEÑA
class RecuperarContrasenaView(APIView):
    """
    API para enviar un correo de recuperación de contraseña
    a un usuario según su email.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        try:
            user = Usuario.objects.get(email=email)
        except Usuario.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        
        # Generar token de recuperación
        token = PasswordResetTokenGenerator().make_token(user)
        reset_link = f"http://localhost:3000/reset-password/{user.pk}/{token}"  # frontend maneja el cambio
        
        # Enviar correo de recuperación
        send_mail(
            'Recuperar contraseña',
            f'Usa este link para cambiar tu contraseña: {reset_link}',
            'noreply@mi-vehiculo.com',
            [email],
            fail_silently=False
        )
        return Response({"mensaje": "Se ha enviado un email con instrucciones"}, status=status.HTTP_200_OK)

# CAMBIAR CONTRASEÑA
class CambiarContrasenaView(APIView):
    """
    API para cambiar la contraseña usando un token válido
    enviado por email. No requiere estar autenticado.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        try:
            user = Usuario.objects.get(pk=user_id)
        except Usuario.DoesNotExist:
            return Response({"error": "Usuario no encontrado"}, status=status.HTTP_404_NOT_FOUND)
        
        # Verificar token
        if not PasswordResetTokenGenerator().check_token(user, token):
            return Response({"error": "Token inválido o expirado"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Cambiar contraseña
        user.set_password(new_password)
        user.save()
        return Response({"mensaje": "Contraseña actualizada correctamente"}, status=status.HTTP_200_OK)

# PERFIL DE USUARIO
class UsuarioPerfilView(generics.RetrieveUpdateAPIView):
    """
    API para ver y actualizar el perfil del usuario autenticado.
    """
    serializer_class = UsuarioPerfilSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """
        Retorna el usuario autenticado como objeto
        a actualizar o visualizar.
        """
        return self.request.user
