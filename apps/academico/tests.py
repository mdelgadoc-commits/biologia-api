from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from apps.users.models import PerfilEstudiante

User = get_user_model()

class PerfilEstudianteTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.client.force_authenticate(user=self.user)

    def test_obtener_perfil(self):
        response = self.client.get("/api/estudiante/perfil/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("vidas", response.data)
        self.assertIn("onboarding_completo", response.data)

    def test_actualizar_onboarding(self):
        data = {
            "nombre_perfil": "Biologo2026",
            "edad": 18,
            "nivel_autopercibido": "regular",
            "idioma": "es-PE"
        }
        response = self.client.post("/api/estudiante/perfil/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["onboarding_completo"])
