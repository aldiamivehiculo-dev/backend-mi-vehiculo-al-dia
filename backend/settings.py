from pathlib import Path
from datetime import timedelta
import os
import dj_database_url
import firebase_admin
from firebase_admin import credentials
import json
from dotenv import load_dotenv

# Carga variables de entorno locales (.env) si existen
load_dotenv()

# ==========================================
# 1. CONFIGURACIÓN BÁSICA
# ==========================================
BASE_DIR = Path(__file__).resolve().parent.parent

# En producción (Railway), toma la clave secreta de las variables.
# En local, usa la 'dev-secret-key'.
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

# DEBUG será False en producción si configuras la variable DEBUG=False en Railway.
# Si no existe la variable, asume True (para desarrollo).
DEBUG = os.environ.get("DEBUG", "True") == "True"

ALLOWED_HOSTS = ["*"]


# ==========================================
# 2. APLICACIONES INSTALADAS
# ==========================================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Librerías de terceros
    "rest_framework",
    "corsheaders",          # Fundamental para conectar con Angular
    "rest_framework_simplejwt",

    # Tus Aplicaciones (Backend de Tesis)
    "usuarios",
    "vehiculos",
    "documentos_vehiculo",
    "accesos",
    "fiscalizador",
    "mantenimiento",
    "notificaciones",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # <--- OBLIGATORIO PARA ESTILOS EN RAILWAY
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",       # <--- OBLIGATORIO PARA ANGULAR
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "backend.wsgi.application"


# ==========================================
# 3. BASE DE DATOS (Híbrida)
# ==========================================
# Si hay una variable DATABASE_URL (Railway), usa Postgres.
# Si no (Tu PC), usa SQLite.
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///db.sqlite3',
        conn_max_age=600,
        ssl_require=False
    )
}

# Modelo de usuario personalizado
AUTH_USER_MODEL = "usuarios.Usuario"


# ==========================================
# 4. SEGURIDAD Y CONEXIÓN (CORS / CSRF)
# ==========================================

# Permitir CORS (Lectura de datos desde Angular)
CORS_ALLOW_ALL_ORIGINS = True # Útil para desarrollo, pero abajo especificamos por seguridad

CORS_ALLOWED_ORIGINS = [
    "http://localhost:8100",                      # PC (Ionic Serve)
    "http://localhost",                           # Android (Emulator/Device)
    "capacitor://localhost",                      # Android (Capacitor Native)
    "https://mi-vehiculo-al-dia.web.app",         # Firebase (Producción)
    "https://mi-vehiculo-al-dia.firebaseapp.com", # Firebase (Alternativo)
]

# Permitir CSRF (Formularios y Login POST)
CSRF_TRUSTED_ORIGINS = [
    "https://web-production-057b0.up.railway.app", # Tu Backend Railway
    "https://mi-vehiculo-al-dia.web.app",          # Tu Frontend Firebase
    "https://mi-vehiculo-al-dia.firebaseapp.com",
    "http://localhost:8100",
    "capacitor://localhost",                       # Importante para App Android
]

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]


# ==========================================
# 5. ARCHIVOS ESTÁTICOS (CSS/JS)
# ==========================================
STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Compresión y almacenamiento eficiente para Railway
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# ==========================================
# 6. CONFIGURACIÓN REST FRAMEWORK & JWT
# ==========================================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    )
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=365), # Token dura 1 año (para tesis es cómodo)
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}


# ==========================================
# 7. FIREBASE ADMIN (Notificaciones/Storage)
# ==========================================
FIREBASE_CREDENTIALS_JSON = os.environ.get("FIREBASE_CREDENTIALS_JSON")

if FIREBASE_CREDENTIALS_JSON:
    try:
        cred_dict = json.loads(FIREBASE_CREDENTIALS_JSON)
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred, {
                "storageBucket": "mi-vehiculo-al-dia.firebasestorage.app"
            })
    except Exception as e:
        print(f"Error cargando Firebase: {e}")
else:
    print("Aviso: No se encontraron credenciales de Firebase (FIREBASE_CREDENTIALS_JSON).")


# ==========================================
# 8. IDIOMA Y ZONA HORARIA
# ==========================================
LANGUAGE_CODE = "es-cl"
TIME_ZONE = "America/Santiago"
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
