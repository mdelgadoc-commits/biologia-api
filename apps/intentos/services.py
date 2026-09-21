"""Orquestador del juego del alumno.

En lugar de señales, la invalidación de caché se registra con
transaction.on_commit(...): solo se ejecuta si la transacción llega a
commitearse (si hay rollback, la caché sigue intacta).
"""
from django.db import transaction
from django.utils import timezone

from apps.academico.services import desbloquear_siguiente
from apps.gamificacion.cache_reportes import invalidar_cache_seccion
from apps.gamificacion.calculos import (
    calcular_estrellas_por_vidas,
    calcular_monedas_recompensa,
)
from apps.gamificacion.services import otorgar_estrellas, otorgar_monedas
from apps.intentos.models import IntentoTema, RespuestaEstudiante
from apps.preguntas.seleccion import SeleccionAleatoriaSimple
from apps.preguntas.validadores import ValidadorFactory


class SinPreguntasDisponibles(Exception):
    """El tema aún no tiene preguntas publicadas para armar un juego."""


def iniciar_intento(estudiante, tema) -> IntentoTema:
    """Crea un intento y le asigna las preguntas de la distribución.

    Une repositories -> seleccion -> IntentoTema. Si ya existe un intento
    activo para el mismo tema, lo devuelve para poder retomar el juego.
    """
    activo = IntentoTema.objects.filter(
        estudiante=estudiante, tema=tema, finalizado__isnull=True
    ).first()
    if activo:
        return activo

    preguntas = SeleccionAleatoriaSimple().seleccionar(tema.id)
    if not preguntas:
        raise SinPreguntasDisponibles(
            f"El tema '{tema.titulo}' aún no tiene preguntas activas."
        )

    intento = IntentoTema.objects.create(estudiante=estudiante, tema=tema)
    intento.preguntas_asignadas.set(preguntas)
    return intento


def responder_pregunta(
    intento: IntentoTema,
    pregunta_id: int,
    payload: dict,
    tiempo_respuesta_ms=None,
) -> dict:
    """Evalúa la respuesta y avanza el estado del intento.

    Une validadores -> RespuestaEstudiante -> rachas/vidas -> finalizar_intento.
    Devuelve un dict que la vista transforma en JSON.
    """
    pregunta = intento.preguntas_asignadas.filter(id=pregunta_id).first()
    if pregunta is None:
        raise ValueError("La pregunta no pertenece a este intento.")

    validador = ValidadorFactory.crear(pregunta)
    es_correcta = validador.validar(payload or {})

    RespuestaEstudiante.objects.create(
        intento=intento,
        pregunta=pregunta,
        es_correcta=es_correcta,
        payload=payload or {},
        tiempo_respuesta_ms=tiempo_respuesta_ms,
    )

    if es_correcta:
        intento.racha_errores_actual = 0
    else:
        intento.vidas_restantes = max(0, intento.vidas_restantes - 1)
        intento.racha_errores_actual += 1
        intento.racha_errores_maxima = max(
            intento.racha_errores_maxima, intento.racha_errores_actual
        )
    intento.save(update_fields=[
        "vidas_restantes",
        "racha_errores_actual",
        "racha_errores_maxima",
    ])

    if intento.vidas_restantes == 0:
        finalizar_intento(intento, exitoso=False)
        return {
            "es_correcta": es_correcta,
            "vidas_restantes": 0,
            "intento_finalizado": True,
            "exitoso": False,
        }

    respuestas = RespuestaEstudiante.objects.filter(intento=intento).count()
    if respuestas >= intento.preguntas_asignadas.count():
        finalizar_intento(intento, exitoso=True)
        return {
            "es_correcta": es_correcta,
            "vidas_restantes": intento.vidas_restantes,
            "intento_finalizado": True,
            "exitoso": True,
        }

    return {
        "es_correcta": es_correcta,
        "vidas_restantes": intento.vidas_restantes,
        "intento_finalizado": False,
        "exitoso": None,
    }


def finalizar_intento(intento: IntentoTema, exitoso: bool):
    """Cierra el intento y, si fue exitoso, aplica progreso y recompensas."""
    with transaction.atomic():
        intento.finalizado = timezone.now()
        if exitoso:
            intento.completado = True
        intento.save(update_fields=["finalizado", "completado"])

        if not exitoso:
            return

        estrellas = calcular_estrellas_por_vidas(intento.vidas_restantes)
        otorgar_estrellas(intento.estudiante, intento.tema, estrellas)
        desbloquear_siguiente(intento.estudiante, intento.tema)

        monedas = calcular_monedas_recompensa(estrellas, intento.racha_errores_maxima)
        otorgar_monedas(intento.estudiante, monedas)

        seccion_ids = list(
            intento.estudiante.secciones.values_list("id", flat=True)
        )
        transaction.on_commit(
            lambda: _invalidar_caches(seccion_ids)
        )


def _invalidar_caches(seccion_ids):
    for seccion_id in seccion_ids:
        invalidar_cache_seccion(seccion_id)