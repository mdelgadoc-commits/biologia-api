from rest_framework import serializers
from .models import Pregunta


class PreguntaEstudianteSerializer(serializers.ModelSerializer):
    alternativas = serializers.SerializerMethodField()
    premisas = serializers.SerializerMethodField()
    palabras = serializers.SerializerMethodField()

    class Meta:
        model = Pregunta
        fields = ["id", "tipo", "enunciado", "alternativas", "premisas", "palabras"]

    def get_alternativas(self, obj):
        els = obj.elementos.filter(rol="alternativa").order_by("orden")
        return [{"id": e.id, "texto": e.contenido} for e in els]

    def get_premisas(self, obj):
        return [{"id": e.id, "texto": e.contenido, "orden": e.orden}
                for e in obj.elementos.filter(rol="premisa").order_by("orden")]

    def get_palabras(self, obj):
        els = obj.elementos.filter(rol__in=["hueco", "distractor"]).order_by("?")
        return [{"id": e.id, "texto": e.contenido} for e in els]
