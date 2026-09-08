from rest_framework import serializers
from .utils import determinar_icono_estado


class TemaEstudianteSerializer(serializers.Serializer):
    """Traduce el dict que arma obtener_mapa_etapa() (stateful) en JSON,
    calculando el ícono con una función stateless (determinar_icono_estado)."""

    id = serializers.SerializerMethodField()
    titulo = serializers.SerializerMethodField()
    orden = serializers.SerializerMethodField()
    desbloqueado = serializers.BooleanField()
    completado = serializers.BooleanField()
    estrellas = serializers.IntegerField()
    icono_estado = serializers.SerializerMethodField()

    def get_id(self, obj):
        return obj["tema"].id

    def get_titulo(self, obj):
        return obj["tema"].titulo

    def get_orden(self, obj):
        return obj["tema"].orden

    def get_icono_estado(self, obj):
        # STATELESS: mismo input -> mismo resultado siempre, sin tocar BD
        return determinar_icono_estado(obj["desbloqueado"], obj["completado"])
