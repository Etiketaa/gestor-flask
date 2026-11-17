from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    OrganizationRegisterSerializer,
    LoginSerializer,
    UserSerializer,
)


@method_decorator(csrf_exempt, name='dispatch')
class RegisterOrganizationView(APIView):
    def post(self, request):
        serializer = OrganizationRegisterSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            return Response(
                {
                    'message': 'Organización y usuario creados',
                    'tokens': _tokens_for_user(result['user']),
                    'organization': {
                        'id': result['organization'].id,
                        'name': result['organization'].name,
                        'slug': result['organization'].slug,
                    },
                    'user': UserSerializer(result['user']).data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def _tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            return Response(
                {
                    'message': 'Inicio de sesión exitoso',
                    'tokens': _tokens_for_user(user),
                    'user': UserSerializer(user).data,
                }
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            pass
        logout(request)
        return Response({'message': 'Sesión cerrada'})


@method_decorator(csrf_exempt, name='dispatch')
class MeView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'No autenticado'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({'user': UserSerializer(request.user).data})
