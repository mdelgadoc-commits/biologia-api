from rest_framework import serializers
from .models import Pregunta, ElementoPregunta


class ElementoPreguntaDocenteSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = ElementoPregunta
        fields = ["id", "rol", "contenido", "es_correcto", "orden", "posicion_hueco"]


class PreguntaDocenteSerializer(serializers.ModelSerializer):
    elementos = ElementoPreguntaDocenteSerializer(many=True, required=False)

    class Meta:
        model = Pregunta
        fields = ["id", "tema", "tipo", "enunciado", "dificultad", "activa", "elementos"]

    def validate(self, data):
        tipo = data.get("tipo", getattr(self.instance, "tipo", None))
        elementos = data.get("elementos", [])

        if tipo == "abierta":
            raise serializers.ValidationError(
                "Las preguntas abiertas ya no se soportan; elimínala y vuelve a crearla."
            )

        if not elementos:
            raise serializers.ValidationError(
                "Este tipo de pregunta requiere al menos un elemento (alternativa/premisa/hueco)."
            )

        if tipo in ("contextual", "inferencial"):
            correctas = [e for e in elementos if e.get("rol") == "alternativa" and e.get("es_correcto")]
            if len(correctas) != 1:
                raise serializers.ValidationError(
                    "Debe haber exactamente una alternativa marcada como correcta."
                )

        if tipo in ("vf_premisas", "cuantas_correctas"):
            premisas = [e for e in elementos if e.get("rol") == "premisa"]
            if not premisas:
                raise serializers.ValidationError(
                    "Este tipo requiere al menos un elemento con rol 'premisa'."
                )
            if any(e.get("es_correcto") is None for e in premisas):
                raise serializers.ValidationError(
                    "Cada premisa debe indicar si es verdadera (es_correcto true/false)."
                )
            if tipo == "cuantas_correctas" and not any(e.get("es_correcto") for e in premisas):
                raise serializers.ValidationError(
                    "Al menos una premisa debe ser verdadera (es_correcto true)."
                )

        if tipo == "completar":
            huecos = [e for e in elementos if e.get("rol") == "hueco"]
            if not huecos:
                raise serializers.ValidationError(
                    "El tipo 'completar' requiere al menos un elemento con rol 'hueco'."
                )
            if any(h.get("posicion_hueco") is None for h in huecos):
                raise serializers.ValidationError(
                    "Cada hueco necesita 'posicion_hueco' definida."
                )

        return data

    def create(self, validated_data):
        elementos_data = validated_data.pop("elementos", [])
        validated_data["creado_por"] = self.context["request"].user

        pregunta = Pregunta.objects.create(**validated_data)

        for el in elementos_data:
            el.pop("id", None)
            ElementoPregunta.objects.create(pregunta=pregunta, **el)

        return pregunta

    def update(self, instance, validated_data):
        elementos_data = validated_data.pop("elementos", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if elementos_data is not None:
            instance.elementos.all().delete()
            for el in elementos_data:
                el.pop("id", None)
                ElementoPregunta.objects.create(pregunta=instance, **el)

        return instance


class ElementoPreguntaLecturaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ElementoPregunta
        fields = ["id", "rol", "contenido", "es_correcto", "orden", "posicion_hueco"]


class PreguntaListaDocenteSerializer(serializers.ModelSerializer):
    elementos = ElementoPreguntaLecturaSerializer(many=True, read_only=True)
    tema_titulo = serializers.CharField(source="tema.titulo", read_only=True)

    class Meta:
        model = Pregunta
        fields = ["id", "tema", "tema_titulo", "tipo", "enunciado",
                  "dificultad", "activa", "elementos"]
