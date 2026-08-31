from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.users.permissions import EsEstudiante
from .models import Etapa
from .serializers import EtapaEstudianteSerializer
from .services import asegurar_progreso_inicial


class EtapaActualView(APIView):
    permission_classes = [IsAuthenticated, EsEstudiante]

    def get(self, request):
        estudiante = request.user.perfilestudiante
        etapa = Etapa.objects.first()
        if not etapa:
            return Response({"detail": "No hay etapas cargadas."}, status=404)

        asegurar_progreso_inicial(estudiante, etapa)

        data = EtapaEstudianteSerializer(etapa, context={"estudiante": estudiante}).data
        return Response(data)


class PerfilEstudianteView(APIView):
    permission_classes = [IsAuthenticated, EsEstudiante]

    def get(self, request):
        perfil = request.user.perfilestudiante
        return Response({"vidas": perfil.vidas, "monedas": perfil.monedas})
