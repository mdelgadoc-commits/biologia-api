from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.urls')),
    path('api/estudiante/', include('apps.academico.urls_estudiante')),

    # Única ruta limpia y unificada para el panel docente
    path('api/docente/', include('apps.docente.urls')),
]
