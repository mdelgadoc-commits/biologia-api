from django.db import models
from apps.academico.models import Tema
from apps.users.models import Usuario


class TipoPregunta(models.TextChoices):
    CONTEXTUAL = "contextual", "Contextual (5 alternativas)"
    VF_PREMISAS = "vf_premisas", "V/F con 4 premisas (5 alternativas)"
    CUANTAS_CORRECTAS = "cuantas_correctas", "Cuántas son correctas (4 premisas)"
    INFERENCIAL = "inferencial", "Inferencial (5 alternativas)"
    ABIERTA = "abierta", "Pregunta abierta"
    COMPLETAR = "completar", "Completar oración (arrastrar palabras)"


class Pregunta(models.Model):
    tema = models.ForeignKey(Tema, related_name="preguntas", on_delete=models.CASCADE)
    tipo = models.CharField(max_length=25, choices=TipoPregunta.choices)
    enunciado = models.TextField()
    dificultad = models.PositiveSmallIntegerField(default=1)
    creado_por = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return f"[{self.tipo}] {self.enunciado[:50]}"


class ElementoPregunta(models.Model):
    class Rol(models.TextChoices):
        ALTERNATIVA = "alternativa", "Alternativa"
        PREMISA = "premisa", "Premisa"
        HUECO = "hueco", "Palabra faltante"
        DISTRACTOR = "distractor", "Palabra distractora (no va en ningún hueco)"

    pregunta = models.ForeignKey(Pregunta, related_name="elementos", on_delete=models.CASCADE)
    rol = models.CharField(max_length=15, choices=Rol.choices)
    contenido = models.CharField(max_length=300)
    es_correcto = models.BooleanField(default=False)
    orden = models.PositiveSmallIntegerField(default=0)
    posicion_hueco = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        ordering = ["orden"]

    def __str__(self):
        return f"{self.rol}: {self.contenido[:30]}"


class PreguntaAbierta(models.Model):
    pregunta = models.OneToOneField(Pregunta, on_delete=models.CASCADE, related_name="abierta")
    respuesta_modelo = models.TextField(blank=True)
