from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import VehiculoData, Vehiculo

@admin.register(VehiculoData)
class VehiculoDataAdmin(admin.ModelAdmin):
    list_display = ('patente', 'marca', 'modelo', 'año', 'color')
    search_fields = ('patente', 'marca', 'modelo')

@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ('patente', 'marca', 'modelo', 'año', 'color', 'user')
    search_fields = ('patente', 'marca', 'modelo')
