"""
STATEFUL: el resultado de esta función depende de si YA se llamó antes
con los mismos parámetros dentro de la ventana TTL.

Cada clave que se genera queda registrada por sección, de modo que
invalidar_cache_seccion() puede limpiar TODAS las variantes (con filtro
por tema o 'todos') aunque no se conozcan de antemano.
"""
from django.core.cache import cache
from .reportes import ReporteSeccionService

TTL_SEGUNDOS = 60

_REGISTRO_POR_SECCION = "dashboard:resumen:registro:{seccion_id}"


def _clave_cache(seccion_id: int, tema_id=None) -> str:
    return f"dashboard:resumen:{seccion_id}:{tema_id or 'todos'}"


def _registro(seccion_id: int) -> str:
    return _REGISTRO_POR_SECCION.format(seccion_id=seccion_id)


def _registrar_clave(seccion_id: int, clave: str) -> None:
    claves = set(cache.get(_registro(seccion_id)) or [])
    claves.add(clave)
    cache.set(_registro(seccion_id), claves, TTL_SEGUNDOS)


def obtener_resumen_cacheado(seccion, tema_id=None) -> dict:
    clave = _clave_cache(seccion.id, tema_id)

    resultado = cache.get(clave)
    if resultado is not None:
        return {**resultado, "desde_cache": True}

    servicio = ReporteSeccionService(seccion, tema_id=tema_id)
    resultado = servicio.resumen()
    cache.set(clave, resultado, TTL_SEGUNDOS)
    _registrar_clave(seccion.id, clave)

    return {**resultado, "desde_cache": False}


def invalidar_cache_seccion(seccion_id: int):
    """Limpia el resumen y todas las variantes por tema de la sección."""
    claves = cache.get(_registro(seccion_id)) or []
    if claves:
        cache.delete_many(claves)
    cache.delete(_registro(seccion_id))