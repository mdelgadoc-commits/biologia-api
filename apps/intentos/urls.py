from django.urls import path
from .views import FinalizarIntentoView, IniciarIntentoView, ResponderPreguntaView

urlpatterns = [
    path("intentos/", IniciarIntentoView.as_view(), name="iniciar-intento"),
    path("intentos/<int:intento_id>/responder/", ResponderPreguntaView.as_view(), name="responder-pregunta"),
    path("intentos/<int:intento_id>/finalizar/", FinalizarIntentoView.as_view(), name="finalizar-intento"),
]