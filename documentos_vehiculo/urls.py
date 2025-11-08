from django.urls import path
from .views import ( DocumentoCreateView, DocumentoListView, DocumentoDetailView, DocumentoDeleteView, DocumentoDownloadView, DocumentoActivosPorVehiculoView, DocumentoHistorialPorTipoView, DocumentoEstadoVehiculoView,
)

urlpatterns = [
    # CRUD
    path('agregar/', DocumentoCreateView.as_view(), name='agregar-documento'),
    path('listar/', DocumentoListView.as_view(), name='listar-documentos'),
    path('<int:pk>/', DocumentoDetailView.as_view(), name='ver-documento'),
    path('<int:pk>/eliminar/', DocumentoDeleteView.as_view(), name='eliminar-documento'),
    # Descargar archivo
    path('<int:pk>/descargar/', DocumentoDownloadView.as_view(), name='descargar-documento'),
    # Activos por vehículo
    path('activos/', DocumentoActivosPorVehiculoView.as_view(), name='documentos-activos'),
    # Historial por tipo
    path('historial/', DocumentoHistorialPorTipoView.as_view(), name='historial-documento'),
    # Estado de documentos del vehículo
    path('estado/<int:vehiculo_id>/', DocumentoEstadoVehiculoView.as_view(), name='estado-documentos-vehiculo'),
]
