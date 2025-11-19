"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from usuarios.views import CustomTokenObtainPairView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/usuarios/', include('usuarios.urls')), 
    path('api/vehiculos/', include('vehiculos.urls')),
    path('api/documentos/', include('documentos_vehiculo.urls')),
    path("api/accesos/", include("accesos.urls")),
    path("api/fiscalizador/", include("fiscalizador.urls")),
    path("api/mantenimiento/", include("mantenimiento.urls")),
    path("api/notificaciones/", include("notificaciones.urls")),


    
     #JWT
    path('api/token/', CustomTokenObtainPairView.as_view(),name='token_obtain_pair'),# login
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),# refrescar token
     
]
     
