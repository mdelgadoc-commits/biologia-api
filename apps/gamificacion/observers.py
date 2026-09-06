"""
Funciones STATELESS (puras): mismo input -> mismo output siempre.
No acceden a la base de datos, no dependen de llamadas anteriores,
no tienen efectos secundarios. Por eso son las más fáciles de testear.
"""


def calcular_estrellas_por_vidas(vidas_restantes: int) -> int:
    """3 estrellas: terminó con 5 o 4 vidas. 2: con 3 o 2. 1: con 1. 0: sin vidas."""
    if vidas_restantes >= 4:
        return 3
    if vidas_restantes >= 2:
        return 2
    if vidas_restantes >= 1:
        return 1
    return 0


def calcular_monedas_recompensa(estrellas: int, racha_errores_maxima: int) -> int:
    """Monedas base por estrella, penalizadas si hubo rachas largas de error."""
    BASE_POR_ESTRELLA = 10
    PENALIZACION_POR_RACHA = 1

    monedas = estrellas * BASE_POR_ESTRELLA
    penalizacion = min(monedas, racha_errores_maxima * PENALIZACION_POR_RACHA)
    return max(0, monedas - penalizacion)


# --- Invalidation de caché al completar intentos ---
from .cache_reportes import invalidar_cache_seccion

@receiver(tema_completado)
def invalidar_cache_dashboard(sender, estudiante, tema, intento, estrellas, **kwargs):
    for seccion in estudiante.secciones.all():
        invalidar_cache_seccion(seccion.id)
