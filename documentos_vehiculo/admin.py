from django.contrib import admin
from .models import DocumentoVehicular

@admin.register(DocumentoVehicular)
class DocumentoVehicularAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "vehiculo", "tipo", "fecha_vencimiento", "activo", "fecha_subida")
    list_filter = ("tipo", "activo", "fecha_vencimiento", "fecha_subida")
    search_fields = ("vehiculo__patente", "user__email", "tipo")
    autocomplete_fields = ("vehiculo", "user")
