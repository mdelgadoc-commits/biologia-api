import random

from rest_framework import serializers

from apps.preguntas.models import ElementoPregunta, Pregunta


class ElementoIntentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElementoPregunta
        # 'es_correcto' se oculta a propósito: el alumno no debe ver la respuesta.
        fields = ["id", "rol", "contenido", "orden", "posicion_hueco"]


class PreguntaIntentoSerializer(serializers.ModelSerializer):
    elementos = serializers.SerializerMethodField()

    class Meta:
        model = Pregunta
        fields = ["id", "tipo", "enunciado", "dificultad", "elementos"]

    def get_elementos(self, obj):
        elementos = list(obj.elementos.all())
        # Baraja alternativas y distractores (no premisas ni huecos, que tienen
        # un orden lógico) para que cada alumno vea opciones en distinto orden.
        grupos = {}
        for e in elementos:
            grupos.setdefault(e.rol, []).append(e)
        resultado = []
        for rol, items in grupos.items():
            if rol in ("alternativa", "distractor"):
                random.shuffle(items)
            resultado.extend(items)
        return ElementoIntentoSerializer(resultado, many=True).data