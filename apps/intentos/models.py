from django.db import models
from django.utils import timezone
from apps.academico.models import Tema
from apps.users.models import PerfilEstudiante
from apps.preguntas.models import Pregunta


class IntentoTema(models.Model):
    estudiante = models.ForeignKey(PerfilEstudiante, on_delete=models.CASCADE, related_name="intentos")
    tema = models.ForeignKey(Tema, on_delete=models.CASCADE)
    iniciado = models.DateTimeField(auto_now_add=True)
    finalizado = models.DateTimeField(null=True, blank=True)
    vidas_restantes = models.PositiveSmallIntegerField(default=5)
    completado = models.BooleanField(default=False)
    racha_errores_actual = models.PositiveSmallIntegerField(default=0)
    racha_errores_maxima = models.PositiveSmallIntegerField(default=0)
    preguntas_asignadas = models.ManyToManyField(Pregunta, related_name="intentos")

    @property
    def esta_activo(self) -> bool:
        return self.finalizado is None and self.vidas_restantes > 0 and not self.completado


class RespuestaEstudiante(models.Model):
    intento = models.ForeignKey(IntentoTema, related_name="respuestas", on_delete=models.CASCADE)
    pregunta = models.ForeignKey(Pregunta, on_delete=models.CASCADE)
    es_correcta = models.BooleanField()
    payload = models.JSONField()   # ids de alternativa, o mapa hueco->palabra
    tiempo_respuesta_ms = models.PositiveIntegerField(null=True, blank=True)
    creado = models.DateTimeField(auto_now_add=True)
