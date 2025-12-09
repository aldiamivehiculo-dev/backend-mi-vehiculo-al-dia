from pathlib import Path
from datetime import timedelta
import os
import firebase_admin
from firebase_admin import credentials
import json
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ======================================================
# CONFIG GENERAL
# ======================================================
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
DEBUG = os.environ.get("DEBUG", "True") == "True"

# 🔥 IMPORTANTE: Dominios permitidos para el backend
ALLOWED_HOSTS = [
    "web-production-057b0.up.railway.app",   # Backend Railway
    "localhost",
    "127.0.0.1",
    "mi-vehiculo-al-dia.web.app",            # Frontend Firebase Hosting
    "mi-vehiculo-al-dia.firebaseapp.com",
]

# 🔥 CSRF permitido (obligatorio para POST desde frontend)
CSRF_TRUSTED_ORIGINS = [
    "https://web-production-057b0.up.railway.app",
    "https://mi-vehiculo-al-dia.web.app",
    "https://mi-vehiculo-al-dia.firebaseapp.com",
]

# ======================================================
# FIREBASE STORAGE
# ======================================================
FIREBASE_CREDENTIALS_JSON = os.environ.get("FIREBASE_CREDENTIALS_JSON")

if FIREBASE_CREDENTIALS_JSON:
    cred_dict = json.loads(FIREBASE_CREDENTIALS_JSON)

    if not firebase_admin._apps:
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred, {
            "storageBucket": "mi-vehiculo-al-dia.firebasestorage.app"
        })
else:
    print("No se cargaron credenciales Firebase (FIREBASE_CREDENTIALS_JSON no existe)")

# ======================================================
# APPS
# ======================================================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "rest_framework",
    "corsheaders",

    "usuarios",
    "vehiculos",
    "documentos_vehiculo",
    "accesos",
    "fiscalizador",
    "mantenimiento",
    "notificaciones",
]

AUTH_USER_MODEL = "usuarios.Usuario"

# ======================================================
# JWT
# ======================================================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    )
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=365),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}

# ======================================================
# MIDDLEWARE
# ======================================================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # ← Importante colocar arriba
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ======================================================
# CORS (PERMITIR PETICIONES)
# ======================================================

# Permite TODOS los orígenes — útil en desarrollo y apps móviles
CORS_ALLOW_ALL_ORIGINS = True

# Aun así, dejo la lista recomendada para mayor seguridad futura
CORS_ALLOWED_ORIGINS = [
    "https://mi-vehiculo-al-dia.web.app",
    "https://mi-vehiculo-al-dia.firebaseapp.com",
    "http://localhost:8100",      # Ionic local
    "http://localhost:5173",
]

# ======================================================
# TEMPLATES
# ======================================================
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

# ======================================================
# BASE DE DATOS (LOCAL / PRODUCCIÓN)
# ======================================================
if DEBUG:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    DATABASES = {
        "default": dj_database_url.parse(
            os.getenv("DATABASE_URL"),
            conn_max_age=600,
            ssl_require=False
        )
    }

# ======================================================
# STATIC FILES
# ======================================================
STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
