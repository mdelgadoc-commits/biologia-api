from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.users.models import PerfilEstudiante
from apps.users.serializers_onboarding import PerfilEstudianteSerializer

class PerfilEstudianteView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        perfil, _ = PerfilEstudiante.objects.get_or_create(usuario=request.user)
        return Response(PerfilEstudianteSerializer(perfil).data)

    def post(self, request):
        perfil, _ = PerfilEstudiante.objects.get_or_create(usuario=request.user)
        serializer = PerfilEstudianteSerializer(perfil, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(PerfilEstudianteSerializer(perfil).data, status=200)

    def patch(self, request):
        return self.post(request)

class EtapaTemasView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response([])
