from django.core.management.base import BaseCommand
from vehiculos.models import VehiculoData, TIPO_CHOICES
import random


class Command(BaseCommand):
    help = "Genera 50 vehículos de ejemplo para la base interna (VehiculoData)."

    def handle(self, *args, **options):
        marcas = ['Toyota', 'Hyundai', 'Kia', 'Chevrolet', 'Nissan', 'Suzuki', 'Ford', 'Peugeot', 'Mazda', 'Honda']
        modelos = ['Yaris', 'Accent', 'Rio', 'Spark', 'Sentra', 'Swift', 'Focus', '208', 'CX-5', 'Civic']
        colores = ['Rojo', 'Blanco', 'Negro', 'Gris', 'Azul', 'Verde', 'Plata', 'Beige']

        VehiculoData.objects.all().delete()  # Limpia los datos anteriores

        tipos_validos = [choice[0] for choice in TIPO_CHOICES]  # ['auto','moto','camion','bus']

        for i in range(50):
            marca = random.choice(marcas)
            modelo = random.choice(modelos)
            color = random.choice(colores)
            año = random.randint(2005, 2023)
            tipo = random.choice(tipos_validos)

            patente = (
                f"{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}"
                f"{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}-"
                f"{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}"
                f"{random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')}-"
                f"{random.randint(10,99)}"
            )

            VehiculoData.objects.create(
                patente=patente,
                marca=marca,
                modelo=modelo,
                año=año,
                color=color,
                tipo=tipo
            )

        self.stdout.write(self.style.SUCCESS("✅ Se han generado 50 vehículos de ejemplo."))
