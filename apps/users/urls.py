from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegistroEstudianteView, RolTokenObtainPairView

urlpatterns = [
    path("login/", RolTokenObtainPairView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("registro/", RegistroEstudianteView.as_view(), name="registro"),
    path("perfil/", PerfilEstudianteView.as_view(), name="perfil-estudiante"),
]
