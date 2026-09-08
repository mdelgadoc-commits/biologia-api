from django.urls import path
from .views import EtapaTemasView

urlpatterns = [
    path("etapas/<int:etapa_id>/temas/", EtapaTemasView.as_view(), name="etapa-temas"),
]
