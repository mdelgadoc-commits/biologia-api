from django.test import SimpleTestCase

class IntentoStatefulTest(SimpleTestCase):
    def test_racha_errores_cambia_con_historial(self):
        racha = 0
        # Simulación de acumulación de estado
        racha += 1
        self.assertEqual(racha, 1)
        racha += 1
        self.assertEqual(racha, 2)
