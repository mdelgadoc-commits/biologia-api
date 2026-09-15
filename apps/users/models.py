from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.validators import RegexValidator

class Usuario(AbstractUser):
    class Rol(models.TextChoices):
        ESTUDIANTE = "estudiante", "Estudiante"
        DOCENTE = "docente", "Docente"

    rol = models.CharField(max_length=20, choices=Rol.choices, default=Rol.ESTUDIANTE)

class PerfilDocente(models.Model):
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="perfildocente")

    def __str__(self):
        return f"Perfil Docente de {self.usuario.username}"

class PerfilEstudiante(models.Model):
    class NivelAutopercibido(models.TextChoices):
        BUENO = "bueno", "Bueno"
        REGULAR = "regular", "Regular"
        MALO = "malo", "Malo"

    class Idioma(models.TextChoices):
        ES_ES = "es-ES", "Español (España)"
        ES_PE = "es-PE", "Español (Perú)"
        EN = "en", "English"

    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="perfilestudiante")
    vidas = models.PositiveIntegerField(default=5)
    monedas = models.PositiveIntegerField(default=0)

    nombre_perfil = models.CharField(
        max_length=30, blank=True,
        validators=[RegexValidator(r'^[a-zA-Z0-9]+$', "Solo letras y números, sin espacios.")]
    )
    edad = models.PositiveSmallIntegerField(null=True, blank=True)
    nivel_autopercibido = models.CharField(
        max_length=10, choices=NivelAutopercibido.choices, blank=True
    )
    idioma = models.CharField(max_length=5, choices=Idioma.choices, default=Idioma.ES_ES)

    @property
    def onboarding_completo(self) -> bool:
        return bool(self.nombre_perfil and self.edad and self.nivel_autopercibido)

    def __str__(self):
        return f"Perfil de {self.usuario.username}"
