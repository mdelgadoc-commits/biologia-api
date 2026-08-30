from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RolTokenObtainPairSerializer


class RolTokenObtainPairView(TokenObtainPairView):
    serializer_class = RolTokenObtainPairSerializer
