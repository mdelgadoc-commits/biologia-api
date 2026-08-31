from .models import Tema, ProgresoTema


def desbloquear_siguiente(estudiante, tema_completado):
    siguiente = Tema.objects.filter(tema_previo=tema_completado).first()
    if siguiente:
        ProgresoTema.objects.update_or_create(
            estudiante=estudiante, tema=siguiente, defaults={"desbloqueado": True}
        )


def asegurar_progreso_inicial(estudiante, etapa):
    primer_tema = etapa.temas.filter(tema_previo__isnull=True).first()
    if primer_tema:
        ProgresoTema.objects.get_or_create(
            estudiante=estudiante, tema=primer_tema, defaults={"desbloqueado": True}
        )
