from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from apps.academico.models import Tema
from apps.intentos.models import IntentoTema
from apps.intentos.services import (
    SinPreguntasDisponibles,
    finalizar_intento,
    iniciar_intento,
    responder_pregunta,
)
from apps.intentos.serializers import PreguntaIntentoSerializer
from apps.users.models import PerfilEstudiante
from apps.users.permissions import EsEstudiante


class IniciarIntentoView(APIView):
    permission_classes = [IsAuthenticated, EsEstudiante]

    def post(self, request):
        perfil = get_object_or_404(PerfilEstudiante, usuario=request.user)

        tema_id = request.data.get("tema_id")
        if not tema_id:
            return Response(
                {"detail": "Se requiere 'tema_id'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        tema = get_object_or_404(Tema, id=tema_id)

        try:
            intento = iniciar_intento(perfil, tema)
        except SinPreguntasDisponibles as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        preguntas = list(intento.preguntas_asignadas.select_related("tema"))
        return Response({
            "intento_id": intento.id,
            "tema": {
                "id": tema.id,
                "titulo": tema.titulo,
                "etapa": tema.etapa.titulo,
            },
            "vidas_restantes": intento.vidas_restantes,
            "ya_tenia_respuestas": intento.respuestas.exists(),
            "preguntas": PreguntaIntentoSerializer(preguntas, many=True).data,
        })


class ResponderPreguntaView(APIView):
    permission_classes = [IsAuthenticated, EsEstudiante]

    def post(self, request, intento_id):
        perfil = get_object_or_404(PerfilEstudiante, usuario=request.user)
        intento = get_object_or_404(IntentoTema, id=intento_id, estudiante=perfil)

        if not intento.esta_activo:
            return Response(
                {"detail": "Este intento ya terminó."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        pregunta_id = request.data.get("pregunta_id")
        if not pregunta_id:
            return Response(
                {"detail": "Se requiere 'pregunta_id'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            resultado = responder_pregunta(
                intento,
                pregunta_id,
                request.data.get("payload", {}),
                request.data.get("tiempo_respuesta_ms"),
            )
        except ValueError as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(resultado)


class FinalizarIntentoView(APIView):
    permission_classes = [IsAuthenticated, EsEstudiante]

    def post(self, request, intento_id):
        perfil = get_object_or_404(PerfilEstudiante, usuario=request.user)
        intento = get_object_or_404(IntentoTema, id=intento_id, estudiante=perfil)

        if intento.finalizado:
            return Response(
                {"detail": "Este intento ya terminó."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        exitoso = bool(request.data.get("exitoso", False))
        finalizar_intento(intento, exitoso=exitoso)
        return Response({
            "finalizado": True,
            "completado": intento.completado,
        })