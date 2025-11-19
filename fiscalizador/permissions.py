from rest_framework.permissions import BasePermission

class IsFiscalizador(BasePermission):
    """
    Permiso que permite acceso solo a usuarios con rol 'fiscalizador'.
    """

    def has_permission(self, request, view):
        # Debe estar autenticado Y tener rol fiscalizador
        return (
            request.user.is_authenticated
            and getattr(request.user, "rol", None) == "fiscalizador"
        )
