from django.urls import path
from .views_reportes import (
    ResumenDashboardView,
    ConceptosCriticosView,
    HeatmapRendimientoView,
    EvolucionMensualView,
    EvolucionIndividualView,
)

urlpatterns = [
    path("dashboard/resumen/", ResumenDashboardView.as_view()),
    path("dashboard/conceptos-criticos/", ConceptosCriticosView.as_view()),
    path("dashboard/heatmap/", HeatmapRendimientoView.as_view()),
    path("dashboard/evolucion/", EvolucionMensualView.as_view()),
    path("dashboard/evolucion/<int:estudiante_id>/", EvolucionIndividualView.as_view()),
]
