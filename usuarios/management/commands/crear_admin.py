from django.core.management.base import BaseCommand
from usuarios.models import Usuario


class Command(BaseCommand):
    help = "Crea un superusuario automáticamente si no existe"

    def handle(self, *args, **kwargs):
        email = "admin@mivehiculo.com"

        if Usuario.objects.filter(email=email).exists():
            self.stdout.write(self.style.WARNING("El superusuario ya existe."))
            return

        Usuario.objects.create_superuser(
            rut="11163969-8",
            email=email,
            nombre="Administrador",
            password="Admin123."
        )

        self.stdout.write(self.style.SUCCESS("Superusuario creado exitosamente."))
