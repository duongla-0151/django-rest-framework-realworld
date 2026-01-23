"""
Views for users app.

Provides API endpoints for user management.
"""
from rest_framework import generics, status
from rest_framework.response import Response

from .models import User
from .serializers import UserSerializer


class UserListCreateAPIView(generics.ListCreateAPIView):
    """
    GET  /api/users/  - List all users
    POST /api/users/  - Create a new user (registration)
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    """
    GET   /api/users/:id/  - Retrieve user by ID
    PUT   /api/users/:id/  - Update user
    PATCH /api/users/:id/  - Partial update user
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
