from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from apps.users.models import PerfilEstudiante
from apps.users.permissions import EsEstudiante
from apps.users.serializers_onboarding import PerfilEstudianteSerializer

from .models import Etapa
from .serializers import TemaEstudianteSerializer
from .services import asegurar_progreso_inicial, obtener_mapa_etapa
from .utils import calcular_progreso_porcentaje




class EtapaTemasView(APIView):
    permission_classes = [IsAuthenticated, EsEstudiante]

    def get(self, request, etapa_id):
        etapa = get_object_or_404(Etapa, id=etapa_id)
        perfil = PerfilEstudiante.objects.filter(usuario=request.user).first()
        if perfil is None:
            return Response(
                {"detail": "Tu cuenta de estudiante no tiene un perfil configurado. "
                           "Contacta a tu docente."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # STATEFUL: garantiza que el primer tema esté desbloqueado (lee y escribe BD)
        asegurar_progreso_inicial(perfil, etapa)

        # STATEFUL: lee el progreso real del estudiante desde la BD
        mapa = obtener_mapa_etapa(perfil, etapa)

        data = TemaEstudianteSerializer(mapa, many=True).data
        completados = sum(1 for m in mapa if m["completado"])
        # STATELESS: puro cálculo aritmético, no toca la BD
        porcentaje = calcular_progreso_porcentaje(len(mapa), completados)

        return Response({
            "etapa": etapa.titulo,
            "progreso_porcentaje": porcentaje,
            "temas": data,
        })