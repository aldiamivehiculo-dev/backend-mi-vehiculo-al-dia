from pathlib import Path
from datetime import timedelta
import os
import firebase_admin
from firebase_admin import credentials
import json
import dj_database_url


BASE_DIR = Path(__file__).resolve().parent.parent


# CONFIG GENERAL
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
DEBUG = os.environ.get("DEBUG", "True") == "True"

ALLOWED_HOSTS = ["*"]


# FIREBASE STORAGE
# FIREBASE STORAGE (PRODUCCIÓN + DESARROLLO)
FIREBASE_CREDENTIALS_JSON = os.environ.get("FIREBASE_CREDENTIALS_JSON")

if FIREBASE_CREDENTIALS_JSON:
    # CREDENCIALES DESDE VARIABLE DE ENTORNO (RAILWAY)
    cred_dict = json.loads(FIREBASE_CREDENTIALS_JSON)

    if not firebase_admin._apps:
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred, {
            "storageBucket": "mi-vehiculo-al-dia.firebasestorage.app"
        })
else:
    print("No se cargaron credenciales Firebase (FIREBASE_CREDENTIALS_JSON no existe)")


# APPS
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

# JWT
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    )
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=365),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}

# MIDDLEWARE
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


CORS_ALLOW_ALL_ORIGINS = True

# TEMPLATES / WSGI
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



# BASE DE DATOS (LOCAL + PRODUCCIÓN)
# →LOCAL: SQLite
# PRODUCCIÓN: Railway usa DATABASE_URL automáticamente

if DEBUG:
    #MODO DESARROLLO → SQLite
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
else:
    #MODO PRODUCCIÓN → PostgreSQL (Railway)
    DATABASES = {
        "default": dj_database_url.config(
            default=os.environ.get("DATABASE_URL"),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }

# STATIC FILES
STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")


# DEFAULTS
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
