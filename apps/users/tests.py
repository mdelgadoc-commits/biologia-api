from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from .models import Usuario


class RegistroEstudianteTests(APITestCase):
    URL = "/api/auth/registro/"

    def datos_validos(self):
        return {
            "username": "JGX-48213",
            "password": "AbCdefg1",
            "nombre": "Ana María Quispe",
            "edad": 15,
            "fecha_nacimiento": "31/12/2009",
            "horas_minimas": "2.5",
            "via_contacto": "email",
            "correo": "ana@ejemplo.pe",
            "telefono": "",
        }

    def test_registro_crea_usuario_y_perfil(self):
        response = self.client.post(self.URL, self.datos_validos(), format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["username"], "JGX-48213")
        self.assertEqual(response.data["rol"], "estudiante")

        usuario = Usuario.objects.get(username="JGX-48213")
        self.assertEqual(usuario.rol, "estudiante")
        self.assertTrue(usuario.check_password("AbCdefg1"))

        perfil = usuario.perfilestudiante
        self.assertEqual(perfil.nombre_perfil, "Ana María Quispe")
        self.assertEqual(perfil.edad, 15)
        self.assertEqual(perfil.horas_minimas, 2.5)
        self.assertEqual(perfil.correo, "ana@ejemplo.pe")
        self.assertEqual(str(perfil.fecha_nacimiento), "2009-12-31")

    def test_telefono_en_lugar_de_correo(self):
        datos = self.datos_validos()
        datos.update(via_contacto="telefono", correo="", telefono="999 111 222")
        response = self.client.post(self.URL, datos, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["perfil"]["telefono"], "999 111 222")

    def test_id_duplicado_rechazado(self):
        self.client.post(self.URL, self.datos_validos(), format="json")
        response = self.client.post(self.URL, self.datos_validos(), format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)

    def test_contraseña_invalida_rechazada(self):
        datos = self.datos_validos()
        datos["password"] = "abcdefg"
        response = self.client.post(self.URL, datos, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_id_formato_invalido_rechazado(self):
        datos = self.datos_validos()
        datos["username"] = "abc-123"
        response = self.client.post(self.URL, datos, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", response.data)

    def test_fecha_invalida_rechazada(self):
        datos = self.datos_validos()
        datos["fecha_nacimiento"] = "31/13/2009"
        response = self.client.post(self.URL, datos, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("fecha_nacimiento", response.data)