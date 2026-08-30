from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class RolTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["rol"] = user.rol
        return token
