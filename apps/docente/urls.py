from django.urls import path, include

urlpatterns = [
    path('', include('apps.academico.urls_docente')),
    path('', include('apps.preguntas.urls_docente')),
    path('', include('apps.gamificacion.urls_docente')),
]
