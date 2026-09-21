"""Acciones de gamificación que PERSISTEN estado (estrellas y monedas)."""
from apps.academico.models import ProgresoTema


def otorgar_estrellas(estudiante, tema, estrellas):
    """Crea/actualiza el progreso del tema guardando el mejor resultado."""
    progreso, _ = ProgresoTema.objects.get_or_create(
        estudiante=estudiante,
        tema=tema,
    )
    if estrellas > progreso.estrellas:
        progreso.estrellas = estrellas
        progreso.completado = True
        progreso.save(update_fields=["estrellas", "completado"])


def otorgar_monedas(estudiante, cantidad):
    """Acumula monedas en el perfil del estudiante."""
    if cantidad <= 0:
        return
    estudiante.monedas += cantidad
    estudiante.save(update_fields=["monedas"])