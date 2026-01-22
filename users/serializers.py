"""
Serializers for users app.
"""

from rest_framework import serializers
from .models import User
from constants import USER_IMAGE_URL_MAX_LENGTH, USER_BIO_DEFAULT
from rest_framework_simplejwt.tokens import RefreshToken


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.

    Handles user creation and updates.
    Password is write-only for security.
    """
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True,
        required=True
    )

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'password',
            'bio',
            'image',
            'date_joined',
        ]
        read_only_fields = ('id', 'date_joined')

    def create(self, validated_data):
        """Create user with properly hashed password. Password is required."""
        password = validated_data.pop('password', None)
        if not password:
            raise serializers.ValidationError({'password': 'Password is required for registration.'})
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        """Update user, hashing password if provided."""
        password = validated_data.pop('password', None)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        if password is not None:
            instance.set_password(password)

        instance.save()
        return instance


class AuthUserSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for login/current user endpoints, includes JWT token.
    """
    token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email',
            'username',
            'token',
        ]
        read_only_fields = ('email', 'username', 'token')

    def get_token(self, obj):
        refresh = RefreshToken.for_user(obj)
        return str(refresh.access_token)
