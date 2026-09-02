from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.users.permissions import EsDocente
from .models import Pregunta
from .serializers_docente import PreguntaDocenteSerializer, PreguntaListaDocenteSerializer


class PreguntaDocenteViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, EsDocente]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["tema", "tipo", "activa"]

    def get_queryset(self):
        return Pregunta.objects.filter(creado_por=self.request.user).select_related("tema").prefetch_related("elementos")

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return PreguntaListaDocenteSerializer
        return PreguntaDocenteSerializer
