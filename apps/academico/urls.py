from django.urls import path
from .views import EtapaTemasView, PerfilEstudianteView

urlpatterns = [
    path("etapas/<int:etapa_id>/temas/", EtapaTemasView.as_view(), name="etapas-temas"),
    path("perfil/", PerfilEstudianteView.as_view(), name="perfil-estudiante"),
]