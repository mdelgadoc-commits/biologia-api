from rest_framework.permissions import BasePermission


class EsDocente(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == "docente"


class EsEstudiante(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.rol == "estudiante"
