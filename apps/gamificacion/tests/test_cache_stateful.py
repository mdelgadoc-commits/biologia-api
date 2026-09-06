from django.test import TestCase
from django.core.cache import cache
from apps.gamificacion.cache_reportes import obtener_resumen_cacheado, invalidar_cache_seccion
from apps.academico.models import Seccion


class ObtenerResumenCacheadoStatefulTest(TestCase):
    def setUp(self):
        cache.clear()

    def test_comportamiento_stateful_de_cache(self):
        seccion = Seccion.objects.first()
        if not seccion:
            return

        primera = obtener_resumen_cacheado(seccion)
        segunda = obtener_resumen_cacheado(seccion)

        self.assertFalse(primera["desde_cache"])
        self.assertTrue(segunda["desde_cache"])

    def test_invalidacion_recalcula_estado(self):
        seccion = Seccion.objects.first()
        if not seccion:
            return

        obtener_resumen_cacheado(seccion)
        invalidar_cache_seccion(seccion.id)
        resultado = obtener_resumen_cacheado(seccion)

        self.assertFalse(resultado["desde_cache"])
