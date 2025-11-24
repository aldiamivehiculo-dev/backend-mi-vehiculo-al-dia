from django.urls import path
from .views import GenerateShareQR, SharedAccessInfoView, RevokeSharedAccessView, SharedAccessListView, SharedAccessLogsView, DownloadSharedDocumentView, SharedAccessDetailView
urlpatterns = [
    path("qr/", GenerateShareQR.as_view(), name="share-generate"),
    path("info/<str:token>/", SharedAccessInfoView.as_view(), name="share-info"),
    path("revocar/<uuid:uuid>/", RevokeSharedAccessView.as_view(), name="revocar-access"),
    path("", SharedAccessListView.as_view(), name="listar-accesos"),
    path("logs/<uuid:uuid>/", SharedAccessLogsView.as_view()),
    path("file/<str:token>/<int:doc_id>/", DownloadSharedDocumentView.as_view(), name="share-file"),
    path("detalle/<uuid:uuid>/", SharedAccessDetailView.as_view(), name="acceso-detalle"),


]
