from django.contrib import admin
from .models import Notificacion
# Register your models here.

@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "titulo", "tipo", "leida", "creada_en", "enviada_email")
    list_filter = ("tipo", "leida", "enviada_email", "creada_en")
    search_fields = ("titulo", "mensaje", "user__rut", "user__email")
