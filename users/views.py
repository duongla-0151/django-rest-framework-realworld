"""
Views for users app.

Provides API endpoints for user management.
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate
from .models import User
from .serializers import UserSerializer, AuthUserSerializer


class UserListCreateAPIView(generics.ListCreateAPIView):
    """
    GET  /api/users/  - List all users
    POST /api/users/  - Create a new user (registration)
    Returns AuthUserSerializer (with JWT token) on registration.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        auth_serializer = AuthUserSerializer(user)
        headers = self.get_success_headers(serializer.data)
        return Response(auth_serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class UserRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    """
    GET   /api/users/:id/  - Retrieve user by ID
    PUT   /api/users/:id/  - Update user
    PATCH /api/users/:id/  - Partial update user
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserLoginAPIView(APIView):
    """
    POST /api/users/login - Authenticate user and return JWT token, email, username
    Accepts email and password.
    """
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'errors': {'non_field_errors': ['Invalid credentials']}}, status=400)
        user = authenticate(request, username=user.username, password=password)
        if user is not None:
            serializer = AuthUserSerializer(user)
            return Response(serializer.data)
        return Response({'errors': {'non_field_errors': ['Invalid credentials']}}, status=400)


class CurrentUserAPIView(APIView):
    """
    GET /api/user - Return current authenticated user (JWT required)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = AuthUserSerializer(request.user)
        return Response(serializer.data)
