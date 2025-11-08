from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

# Manager personalizado de Usuario
class UsuarioManager(BaseUserManager):
    """
    Manager para crear usuarios y superusuarios con los campos personalizados.
    """

    def create_user(self, rut, email, nombre, password=None, rol='usuario', **extra_fields):
        """
        Crea y guarda un usuario normal en la base de datos.
        Parámetros:
            rut (str): Identificador único del usuario (RUT chileno).
            email (str): Correo electrónico del usuario.
            nombre (str): Nombre completo del usuario.
            password (str, opcional): Contraseña del usuario.
            rol (str, opcional): Rol del usuario ('usuario' por defecto).
            extra_fields (dict): Otros campos adicionales.
        Retorna:
            Usuario: Instancia del usuario creado.
        """
        if not rut:
            raise ValueError("El usuario debe tener RUT")
        if not email:
            raise ValueError("El usuario debe tener un correo electrónico")
        
        email = self.normalize_email(email)
        usuario = self.model(rut=rut, email=email, nombre=nombre, rol=rol, **extra_fields)
        usuario.set_password(password)  # encripta la contraseña
        usuario.save(using=self._db)
        return usuario

    def create_superuser(self, rut, email, nombre, password=None, **extra_fields):
        """
        Crea y guarda un superusuario en la base de datos.
        Parámetros:
            rut (str): RUT del superusuario.
            email (str): Correo electrónico del superusuario.
            nombre (str): Nombre completo del superusuario.
            password (str): Contraseña.
            extra_fields (dict): Otros campos adicionales.
        Retorna:
            Usuario: Instancia del superusuario creado.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('rol', 'admin')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')

        return self.create_user(rut, email, nombre, password, **extra_fields)
#Modelo personalizado de Usuario
class Usuario(AbstractBaseUser, PermissionsMixin):
    """
    Modelo de usuario personalizado que reemplaza al modelo por defecto de Django.
    """

    ROLES = (
        ('usuario', 'Usuarios'),
        ('fiscalizador', 'Fiscalizador'),
        ('admin', 'Administrador App')
    )

    rut = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=150)
    apellidos = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    rol = models.CharField(max_length=20, choices=ROLES, default='usuario')
    fecha_nacimiento = models.DateField(null=True, blank=True)
    residencia = models.CharField(max_length=255, blank=True)
    telefono = models.CharField(max_length=11, blank=True)
    
    #  CAMPO AGREGADO: Necesario para la restricción de 30 días en el Serializer
    fecha_nacimiento_ultima_actualizacion = models.DateTimeField(null=True, blank=True) 
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    # Asociamos el manager personalizado
    objects = UsuarioManager()

    # Campos de login
    USERNAME_FIELD = 'rut'
    REQUIRED_FIELDS = ['email', 'nombre']

    def __str__(self):
        """
        Retorna una representación legible del usuario.
        """
        return f"{self.nombre} ({self.rut})"