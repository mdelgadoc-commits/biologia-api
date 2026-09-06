from django.urls import path
from .views_secciones import SeccionesDocenteView, EstudiantesSeccionView

urlpatterns = [
    path("secciones/", SeccionesDocenteView.as_view()),
    path("secciones/<int:seccion_id>/estudiantes/", EstudiantesSeccionView.as_view()),
]
