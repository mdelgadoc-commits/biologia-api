import re
from datetime import date

from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import PerfilEstudiante
from .validators import RegexPasswordValidator

Usuario = get_user_model()

REGEX_ID = r"^[A-Z]{3}-\d{5}$"
REGEX_NOMBRE = r"^(?:[^\W\d_]|[ \-\']){2,100}$"
REGEX_FECHA = r"^(\d{2})/(\d{2})/(\d{4})$"
REGEX_HORAS = r"^\d+(\.\d+)?$"
REGEX_CORREO = r"^[^\s@]+@[^\s@]+\.[^\s@]{2,}$"


class RegistroEstudianteSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=9)
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    nombre = serializers.CharField(max_length=100)
    edad = serializers.IntegerField(min_value=1, max_value=120)
    fecha_nacimiento = serializers.CharField()
    horas_minimas = serializers.CharField()
    via_contacto = serializers.ChoiceField(choices=[c for c, _ in PerfilEstudiante.ViaContacto.choices])
    correo = serializers.CharField(required=False, allow_blank=True)
    telefono = serializers.CharField(required=False, allow_blank=True)

    def validate_username(self, value):
        codigo = value.strip().upper()
        if not re.fullmatch(REGEX_ID, codigo):
            raise serializers.ValidationError("El ID debe tener el formato XXX-00000.")
        if Usuario.objects.filter(username=codigo).exists():
            raise serializers.ValidationError("Ese ID ya está registrado.")
        return codigo

    def validate_password(self, value):
        RegexPasswordValidator().validate(value)
        return value

    def validate_nombre(self, value):
        nombre = value.strip()
        if not re.fullmatch(REGEX_NOMBRE, nombre):
            raise serializers.ValidationError("Nombre inválido. Usa solo letras y espacios.")
        return nombre

    def validate_fecha_nacimiento(self, value):
        partes = re.fullmatch(REGEX_FECHA, value.strip())
        if not partes:
            raise serializers.ValidationError("Usa el formato DD/MM/AAAA.")
        dia, mes, anio = map(int, partes.groups())
        if anio < 1900:
            raise serializers.ValidationError("Año inválido.")
        try:
            fecha = date(anio, mes, dia)
        except ValueError:
            raise serializers.ValidationError("Fecha inválida.")
        if fecha > date.today():
            raise serializers.ValidationError("La fecha no puede ser futura.")
        return fecha

    def validate_horas_minimas(self, value):
        horas = value.strip().replace(",", ".")
        if not re.fullmatch(REGEX_HORAS, horas) or float(horas) <= 0:
            raise serializers.ValidationError("Horas inválidas. Ejemplo: 2.5")
        return float(horas)

    def validate(self, attrs):
        via = attrs.get("via_contacto")
        if via == PerfilEstudiante.ViaContacto.EMAIL:
            correo = attrs.get("correo", "").strip()
            if not re.fullmatch(REGEX_CORREO, correo):
                raise serializers.ValidationError({"correo": "Correo inválido."})
        else:
            digitos = re.sub(r"\D", "", attrs.get("telefono", ""))
            if not (9 <= len(digitos) <= 15):
                raise serializers.ValidationError({"telefono": "Teléfono inválido."})
        return attrs

    def create(self, validated_data):
        username = validated_data.pop("username")
        password = validated_data.pop("password")
        usuario = Usuario.objects.create_user(
            username=username, password=password, rol=Usuario.Rol.ESTUDIANTE
        )
        perfil = PerfilEstudiante(
            usuario=usuario,
            nombre_perfil=validated_data["nombre"],
            edad=validated_data["edad"],
            fecha_nacimiento=validated_data["fecha_nacimiento"],
            horas_minimas=validated_data["horas_minimas"],
            via_contacto=validated_data["via_contacto"],
            correo=validated_data.get("correo", ""),
            telefono=validated_data.get("telefono", ""),
        )
        perfil.save()
        return usuario