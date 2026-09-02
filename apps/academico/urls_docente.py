from django.urls import path
from .views_docente import TemaDocenteListView

urlpatterns = [
    path("temas/", TemaDocenteListView.as_view(), name="docente-temas-list"),
]
