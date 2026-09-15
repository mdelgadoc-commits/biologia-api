from rest_framework import serializers
from .models import PerfilEstudiante

class PerfilEstudianteSerializer(serializers.ModelSerializer):
    onboarding_completo = serializers.BooleanField(read_only=True)

    class Meta:
        model = PerfilEstudiante
        fields = [
            "nombre_perfil", "edad", "nivel_autopercibido", 
            "idioma", "vidas", "monedas", "onboarding_completo"
        ]

    def validate_edad(self, value):
        if value is not None and not (13 <= value <= 25):
            raise serializers.ValidationError("La edad debe estar entre 13 y 25.")
        return value
