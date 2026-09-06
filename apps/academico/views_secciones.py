from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from apps.users.permissions import EsDocente
from .models import Seccion


class SeccionesDocenteView(APIView):
    permission_classes = [IsAuthenticated, EsDocente]

    def get(self, request):
        secciones = Seccion.objects.filter(docente=request.user)
        return Response([{"id": s.id, "nombre": s.nombre} for s in secciones])


class EstudiantesSeccionView(APIView):
    permission_classes = [IsAuthenticated, EsDocente]

    def get(self, request, seccion_id):
        seccion = get_object_or_404(Seccion, id=seccion_id, docente=request.user)
        q = request.query_params.get("q", "")
        estudiantes = seccion.estudiantes.select_related("usuario")
        if q:
            estudiantes = estudiantes.filter(usuario__first_name__icontains=q) | \
                          estudiantes.filter(usuario__last_name__icontains=q)
        return Response([
            {"id": e.id, "nombre": e.usuario.get_full_name() or e.usuario.username}
            for e in estudiantes
        ])
