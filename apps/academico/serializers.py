from rest_framework import serializers
from .models import Etapa, Tema, ProgresoTema


class TemaEstudianteSerializer(serializers.ModelSerializer):
    desbloqueado = serializers.SerializerMethodField()
    completado = serializers.SerializerMethodField()

    class Meta:
        model = Tema
        fields = ["id", "titulo", "orden", "icono", "desbloqueado", "completado"]

    def get_progreso(self, obj):
        estudiante = self.context["estudiante"]
        return ProgresoTema.objects.filter(estudiante=estudiante, tema=obj).first()

    def get_desbloqueado(self, obj):
        progreso = self.get_progreso(obj)
        return bool(progreso and progreso.desbloqueado)

    def get_completado(self, obj):
        progreso = self.get_progreso(obj)
        return bool(progreso and progreso.completado)


class EtapaEstudianteSerializer(serializers.ModelSerializer):
    temas = serializers.SerializerMethodField()

    class Meta:
        model = Etapa
        fields = ["id", "titulo", "orden", "temas"]

    def get_temas(self, obj):
        temas = obj.temas.all()
        return TemaEstudianteSerializer(temas, many=True, context=self.context).data
