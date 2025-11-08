from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from usuarios.models import Usuario

class UsuarioTests(APITestCase):

    def test_crear_usuario(self):
        """
        Test para crear un usuario exitosamente
        """
        url = reverse("registro-usuario")

        data = {
            "nombre": "Andrea",
            "email": "andrea@example.com",
            "rut": "12345678-5",
            "fecha_nacimiento": "2000-01-01",
            "residencia": "Santiago",
            "telefono": "987654321",
            "password": "Test1234.",
            "rol": "usuario"
        }

        response = self.client.post(url, data, format="json")

        # ✅ Respuesta 201
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # ✅ Usuario creado en BD
        self.assertTrue(Usuario.objects.filter(rut="12345678-5").exists())

        user = Usuario.objects.get(rut="12345678-5")

        # ✅ Verificar que datos coinciden
        self.assertEqual(user.nombre, "Andrea")
        self.assertEqual(user.email, "andrea@example.com")

        # ✅ La contraseña debe estar encriptada
        self.assertNotEqual(user.password, "Test1234.")
        self.assertTrue(user.check_password("Test1234."))
