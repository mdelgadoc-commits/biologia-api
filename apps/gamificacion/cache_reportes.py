"""
STATEFUL: el resultado de esta función depende de si YA se llamó antes
con los mismos parámetros dentro de la ventana TTL.
"""
from django.core.cache import cache
from .reportes import ReporteSeccionService

TTL_SEGUNDOS = 60


def _clave_cache(seccion_id: int, tema_id: str | None) -> str:
    return f"dashboard:resumen:{seccion_id}:{tema_id or 'todos'}"


def obtener_resumen_cacheado(seccion, tema_id=None) -> dict:
    clave = _clave_cache(seccion.id, tema_id)

    resultado = cache.get(clave)
    if resultado is not None:
        return {**resultado, "desde_cache": True}

    servicio = ReporteSeccionService(seccion, tema_id=tema_id)
    resultado = servicio.resumen()
    cache.set(clave, resultado, TTL_SEGUNDOS)

    return {**resultado, "desde_cache": False}


def invalidar_cache_seccion(seccion_id: int):
    cache.delete(_clave_cache(seccion_id, None))
