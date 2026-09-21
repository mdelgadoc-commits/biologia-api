from django.test import TestCase
from django.core.cache import cache
from apps.gamificacion.cache_reportes import (
    _clave_cache,
    obtener_resumen_cacheado,
    invalidar_cache_seccion,
)
from apps.academico.models import Seccion
from apps.users.models import Usuario


class ObtenerResumenCacheadoStatefulTest(TestCase):
    def setUp(self):
        cache.clear()
        docente = Usuario.objects.create(username="doc_cache", rol=Usuario.Rol.DOCENTE)
        self.seccion = Seccion.objects.create(nombre="3ro A", docente=docente)

    def test_comportamiento_stateful_de_cache(self):
        primera = obtener_resumen_cacheado(self.seccion)
        segunda = obtener_resumen_cacheado(self.seccion)

        self.assertFalse(primera["desde_cache"])
        self.assertTrue(segunda["desde_cache"])

    def test_invalidacion_recalcula_estado(self):
        obtener_resumen_cacheado(self.seccion)
        invalidar_cache_seccion(self.seccion.id)
        resultado = obtener_resumen_cacheado(self.seccion)

        self.assertFalse(resultado["desde_cache"])

    def test_invalidacion_limpia_todas_las_variantes_por_tema(self):
        obtener_resumen_cacheado(self.seccion)
        obtener_resumen_cacheado(self.seccion, tema_id=7)

        clave_todos = _clave_cache(self.seccion.id, None)
        clave_tema = _clave_cache(self.seccion.id, 7)
        self.assertIsNotNone(cache.get(clave_todos))
        self.assertIsNotNone(cache.get(clave_tema))

        invalidar_cache_seccion(self.seccion.id)

        self.assertIsNone(cache.get(clave_todos))
        self.assertIsNone(cache.get(clave_tema))
        self.assertIsNone(cache.get(f"dashboard:resumen:registro:{self.seccion.id}"))

    def test_variante_por_tema_tambien_se_registra(self):
        obtener_resumen_cacheado(self.seccion, tema_id=7)
        invalidar_cache_seccion(self.seccion.id)
        otra = obtener_resumen_cacheado(self.seccion, tema_id=7)

        self.assertFalse(otra["desde_cache"])