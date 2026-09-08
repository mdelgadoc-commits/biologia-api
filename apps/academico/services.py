from .models import Tema, ProgresoTema


def desbloquear_siguiente(estudiante, tema_completado):
    """STATEFUL: cuando se completa un tema, desbloquea el que lo tiene
    como tema_previo."""
    siguiente = Tema.objects.filter(tema_previo=tema_completado).first()
    if siguiente:
        ProgresoTema.objects.update_or_create(
            estudiante=estudiante, tema=siguiente, defaults={"desbloqueado": True}
        )


def asegurar_progreso_inicial(estudiante, etapa):
    """STATEFUL: al entrar por primera vez a una etapa, desbloquea el primer
    tema (el que no tiene tema_previo)."""
    primer_tema = etapa.temas.filter(tema_previo__isnull=True).first()
    if primer_tema:
        ProgresoTema.objects.get_or_create(
            estudiante=estudiante, tema=primer_tema, defaults={"desbloqueado": True}
        )


def obtener_mapa_etapa(estudiante, etapa):
    """STATEFUL: devuelve los temas de una etapa junto con el progreso
    real del estudiante leído desde la base de datos."""
    temas = Tema.objects.filter(etapa=etapa).select_related("tema_previo")
    progresos = {
        p.tema_id: p
        for p in ProgresoTema.objects.filter(estudiante=estudiante, tema__in=temas)
    }

    resultado = []
    for tema in temas:
        progreso = progresos.get(tema.id)
        resultado.append({
            "tema": tema,
            "desbloqueado": progreso.desbloqueado if progreso else False,
            "completado": progreso.completado if progreso else False,
            "estrellas": progreso.estrellas if progreso else 0,
        })
    return resultado
