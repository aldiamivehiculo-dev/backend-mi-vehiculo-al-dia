from django.utils import timezone
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Notificacion
from .serializers import NotificacionSerializer

class NotificacionListView(generics.ListAPIView):
    """
    Lista notificaciones del usuario autenticado.
    Filtros:
      - ?solo_no_leidas=1
      - ?tipo=documento|mantenimiento|qr|sistema
    """
    serializer_class = NotificacionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Notificacion.objects.filter(user=self.request.user)

        solo_no_leidas = self.request.query_params.get("solo_no_leidas")
        tipo = self.request.query_params.get("tipo")

        if solo_no_leidas == "1":
            qs = qs.filter(leida=False)
        if tipo:
            qs = qs.filter(tipo=tipo)

        return qs


class NotificacionMarcarLeidaView(APIView):
    """
    Marca UNA notificación como leída.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            noti = Notificacion.objects.get(pk=pk, user=request.user)
        except Notificacion.DoesNotExist:
            return Response({"detail": "Notificación no encontrada"}, status=404)

        if not noti.leida:
            noti.leida = True
            noti.leida_en = timezone.now()
            noti.save(update_fields=["leida", "leida_en"])

        return Response({"detail": "Notificación marcada como leída"})


class NotificacionMarcarTodasLeidasView(APIView):
    """
    Marca TODAS las notificaciones del usuario como leídas.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        ahora = timezone.now()
        Notificacion.objects.filter(user=request.user, leida=False).update(
            leida=True,
            leida_en=ahora
        )
        return Response({"detail": "Todas las notificaciones marcadas como leídas"})
