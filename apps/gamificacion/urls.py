from django.urls import path
from .views_reportes import ResumenDashboardView

urlpatterns = [
    path('reportes/resumen/', ResumenDashboardView.as_view(), name='resumen-dashboard'),
]
