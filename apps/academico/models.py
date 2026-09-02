from django.db import models
from apps.users.models import PerfilEstudiante


class Etapa(models.Model):
    titulo = models.CharField(max_length=100)
    orden = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["orden"]

    def __str__(self):
        return self.titulo


class Tema(models.Model):
    etapa = models.ForeignKey(Etapa, related_name="temas", on_delete=models.CASCADE)
    titulo = models.CharField(max_length=100)
    orden = models.PositiveSmallIntegerField()
    tema_previo = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="siguientes"
    )
    icono = models.CharField(max_length=50, blank=True)

    class Meta:
        ordering = ["orden"]

    def __str__(self):
        return f"{self.etapa.titulo} - {self.titulo}"


class ProgresoTema(models.Model):
    estudiante = models.ForeignKey(PerfilEstudiante, on_delete=models.CASCADE, related_name="progresos")
    tema = models.ForeignKey(Tema, on_delete=models.CASCADE)
    desbloqueado = models.BooleanField(default=False)
    completado = models.BooleanField(default=False)
    estrellas = models.PositiveSmallIntegerField(default=0)

    class Meta:
        unique_together = ("estudiante", "tema")

    def __str__(self):
        return f"{self.estudiante} - {self.tema} ({'✓' if self.completado else '…'})"


class Seccion(models.Model):
    """Grupo/clase de un docente, ej. '3ro A Biología'."""
    nombre = models.CharField(max_length=100)
    docente = models.ForeignKey(
        "users.Usuario", on_delete=models.CASCADE, related_name="secciones",
        limit_choices_to={"rol": "docente"}
    )
    estudiantes = models.ManyToManyField(
        "users.PerfilEstudiante", related_name="secciones", blank=True
    )

    def __str__(self):
        return self.nombre
