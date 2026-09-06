from .cache_reportes import obtener_resumen_cacheado
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from apps.users.permissions import EsDocente
from apps.academico.models import Seccion
from .reportes import ReporteSeccionService


def _service_desde_request(request):
    seccion_id = request.query_params.get("seccion")
    tema_id = request.query_params.get("tema")
    seccion = get_object_or_404(Seccion, id=seccion_id, docente=request.user)
    return ReporteSeccionService(seccion, tema_id=tema_id)


class ResumenDashboardView(APIView):
    permission_classes = [IsAuthenticated, EsDocente]

    def get(self, request):
        servicio = _service_desde_request(request)
        return Response(servicio.resumen())


class ConceptosCriticosView(APIView):
    permission_classes = [IsAuthenticated, EsDocente]

    def get(self, request):
        servicio = _service_desde_request(request)
        return Response(servicio.conceptos_criticos())


class HeatmapRendimientoView(APIView):
    permission_classes = [IsAuthenticated, EsDocente]

    def get(self, request):
        servicio = _service_desde_request(request)
        return Response(servicio.heatmap())


class EvolucionMensualView(APIView):
    permission_classes = [IsAuthenticated, EsDocente]

    def get(self, request):
        servicio = _service_desde_request(request)
        top = int(request.query_params.get("top", 5))
        return Response(servicio.evolucion_mensual(top=top))


class EvolucionIndividualView(APIView):
    permission_classes = [IsAuthenticated, EsDocente]

    def get(self, request, estudiante_id):
        servicio = _service_desde_request(request)
        return Response(servicio.evolucion_individual(estudiante_id))


from .reportes import PuntosDebilesService


class PuntosDebilesView(APIView):
    permission_classes = [IsAuthenticated, EsDocente]

    def get(self, request):
        seccion_id = request.query_params.get("seccion")
        seccion = get_object_or_404(Seccion, id=seccion_id, docente=request.user)
        tema_id = request.query_params.get("tema")
        estudiante_id = request.query_params.get("estudiante")

        servicio = PuntosDebilesService(seccion, tema_id=tema_id, estudiante_id=estudiante_id)
        return Response(servicio.calcular())
