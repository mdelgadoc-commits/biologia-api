from django.urls import path
from .views import EtapaActualView, PerfilEstudianteView

urlpatterns = [
    path("etapas/", EtapaActualView.as_view(), name="etapa-actual"),
    path("perfil/", PerfilEstudianteView.as_view(), name="perfil-estudiante"),
]
