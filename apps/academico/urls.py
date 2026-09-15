from django.urls import path
from .views import EtapaTemasView, PerfilEstudianteView

urlpatterns = [
    path("perfil/", PerfilEstudianteView.as_view(), name="perfil-estudiante"),
    path("etapas/", EtapaTemasView.as_view(), name="etapas-temas"),
]
