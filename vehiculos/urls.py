from django.urls import path
from .views import VehiculoCreateView, VehiculoListView, VehiculoDetailView, VehiculoUpdateView,VehiculoDeleteView

urlpatterns = [
    path('agregar/', VehiculoCreateView.as_view(), name='agregar-vehiculo'),
    path('listar/', VehiculoListView.as_view(), name='listar-vehiculo'),
    path('<int:pk>/', VehiculoDetailView.as_view(), name='ver-vehiculo'),
    path('<int:pk>/actualizar/', VehiculoUpdateView.as_view(), name='actualizar'),
    path('<int:pk>/eliminar/', VehiculoDeleteView.as_view(), name='eliminar-vehiculo'),




]