from rest_framework import generics, serializers
from rest_framework.permissions import IsAuthenticated
from apps.users.permissions import EsDocente
from .models import Tema


class TemaSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tema
        fields = ["id", "titulo", "orden"]


class TemaDocenteListView(generics.ListAPIView):
    """Retorna el listado de temas para los selectores/dropdowns en las pantallas del docente."""
    permission_classes = [IsAuthenticated, EsDocente]
    queryset = Tema.objects.all().order_by("orden")
    serializer_class = TemaSimpleSerializer
