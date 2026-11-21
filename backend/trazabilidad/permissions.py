from rest_framework.permissions import BasePermission

from usuarios.models import ROLES_INTERMEDIARIOS


class EsAdministrador(BasePermission):
    message = 'Solo el administrador puede acceder a esta sección.'

    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and u.rol == 'administrador')


class EsIntermediario(BasePermission):
    message = 'Solo distribuidores, acopiadores y transportadores pueden acceder a esta sección.'

    def has_permission(self, request, view):
        u = request.user
        return bool(u and u.is_authenticated and u.rol in ROLES_INTERMEDIARIOS)
