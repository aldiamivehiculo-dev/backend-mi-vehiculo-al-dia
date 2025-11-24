from django.utils import timezone
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Notificacion
from .serializers import NotificacionSerializer

# Vista que lista las notificaciones del usuario autenticado.
class NotificacionListView(generics.ListAPIView):
    serializer_class = NotificacionSerializer
    permission_classes = [permissions.IsAuthenticated]

    #Obtiene las notificaciones filtradas según query params
    def get_queryset(self):
        qs = Notificacion.objects.filter(user=self.request.user)

        solo_no_leidas = self.request.query_params.get("solo_no_leidas")
        tipo = self.request.query_params.get("tipo")

        #Filtro: solo mostrar las no leídas
        if solo_no_leidas == "1":
            qs = qs.filter(leida=False)

        #Filtro por tipo de notificación
        if tipo:
            qs = qs.filter(tipo=tipo)

        return qs
#Vista que marca una sola notificación como leída

class NotificacionMarcarLeidaView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    #Marca la notificación indicada con su PK
    def post(self, request, pk):
        try:
            #Buscar notificación del usuario
            noti = Notificacion.objects.get(pk=pk, user=request.user)
        except Notificacion.DoesNotExist:
            return Response({"detail": "Notificación no encontrada"}, status=404)

        #Si aún no está leída, se actualizan sus campos
        if not noti.leida:
            noti.leida = True
            noti.leida_en = timezone.now()
            noti.save(update_fields=["leida", "leida_en"])

        return Response({"detail": "Notificación marcada como leída"})
#Vista que marca *todas* las notificaciones del usuario como leídas

class NotificacionMarcarTodasLeidasView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    #Marca todas las notificaciones como leídas en un solo POST
    def post(self, request):
        ahora = timezone.now()

        #Actualiza las notificaciones no leídas del usuario
        Notificacion.objects.filter(
            user=request.user,
            leida=False
        ).update(
            leida=True,
            leida_en=ahora
        )

        return Response({"detail": "Todas las notificaciones marcadas como leídas"})
