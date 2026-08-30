from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    class Rol(models.TextChoices):
        DOCENTE = "docente", "Docente"
        ESTUDIANTE = "estudiante", "Estudiante"

    rol = models.CharField(max_length=15, choices=Rol.choices)


class PerfilDocente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    institucion = models.CharField(max_length=150, blank=True)
    puede_publicar_contenido = models.BooleanField(default=True)

    def __str__(self):
        return f"Docente: {self.usuario.username}"


class PerfilEstudiante(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE)
    docente = models.ForeignKey(
        Usuario, null=True, on_delete=models.SET_NULL,
        related_name="estudiantes", limit_choices_to={"rol": "docente"}
    )
    vidas = models.PositiveSmallIntegerField(default=5)
    monedas = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Estudiante: {self.usuario.username}"
