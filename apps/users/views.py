from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RolTokenObtainPairSerializer
from .serializers_registro import RegistroEstudianteSerializer


class RolTokenObtainPairView(TokenObtainPairView):
    serializer_class = RolTokenObtainPairSerializer


class RegistroEstudianteView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistroEstudianteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        usuario = serializer.save()
        perfil = usuario.perfilestudiante
        return Response(
            {
                "id": usuario.id,
                "username": usuario.username,
                "rol": usuario.rol,
                "perfil": {
                    "nombre": perfil.nombre_perfil,
                    "edad": perfil.edad,
                    "fecha_nacimiento": perfil.fecha_nacimiento.strftime("%d/%m/%Y")
                    if perfil.fecha_nacimiento else None,
                    "horas_minimas": perfil.horas_minimas,
                    "via_contacto": perfil.via_contacto,
                    "correo": perfil.correo,
                    "telefono": perfil.telefono,
                },
                "onboarding_completo": perfil.onboarding_completo,
            },
            status=status.HTTP_201_CREATED,
        )
