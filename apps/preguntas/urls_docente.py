from rest_framework.routers import DefaultRouter
from .views_docente import PreguntaDocenteViewSet

router = DefaultRouter()
router.register("preguntas", PreguntaDocenteViewSet, basename="preguntas-docente")

urlpatterns = router.urls
