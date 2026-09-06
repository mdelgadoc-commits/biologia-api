from django.test import SimpleTestCase
from apps.gamificacion.calculos import calcular_estrellas_por_vidas, calcular_monedas_recompensa


class CalculosStatelessTest(SimpleTestCase):
    def test_calcular_estrellas_es_determinista(self):
        resultados = {calcular_estrellas_por_vidas(4) for _ in range(100)}
        self.assertEqual(resultados, {3})

    def test_calcular_estrellas_casos_limite(self):
        self.assertEqual(calcular_estrellas_por_vidas(5), 3)
        self.assertEqual(calcular_estrellas_por_vidas(2), 2)
        self.assertEqual(calcular_estrellas_por_vidas(1), 1)
        self.assertEqual(calcular_estrellas_por_vidas(0), 0)

    def test_calcular_monedas_no_depende_de_llamadas_previas(self):
        primera = calcular_monedas_recompensa(3, 2)
        segunda = calcular_monedas_recompensa(3, 2)
        self.assertEqual(primera, 28)
        self.assertEqual(segunda, 28)

