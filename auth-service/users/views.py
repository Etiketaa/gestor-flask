from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import login, logout
from .serializers import (
    OrganizationRegisterSerializer,
    LoginSerializer,
    UserSerializer,
)


class RegisterOrganizationView(APIView):
    def post(self, request):
        serializer = OrganizationRegisterSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            return Response(
                {
                    'message': 'Organización y usuario creados',
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


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            return Response(
                {
                    'message': 'Inicio de sesión exitoso',
                    'user': UserSerializer(user).data,
                }
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    def post(self, request):
        logout(request)
        return Response({'message': 'Sesión cerrada'})


class MeView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response({'error': 'No autenticado'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response({'user': UserSerializer(request.user).data})
