"""
Serializers for profiles app.

Note: Profile serializers will be implemented in a future phase.
"""
from rest_framework import serializers

from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for Profile model.

    Note: Profile endpoints will be implemented in a future phase.
    """
    username = serializers.CharField(source='user.username', read_only=True)
    bio = serializers.CharField(source='user.bio', read_only=True)
    image = serializers.URLField(source='user.image', read_only=True)
    following = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['username', 'bio', 'image', 'following']

    def get_following(self, obj):
        """Check if the current user follows this profile."""
        request = self.context.get('request')
        if request is None or not request.user.is_authenticated:
            return False

        try:
            current_profile = request.user.profile
            return current_profile.is_following(obj)
        except Profile.DoesNotExist:
            return False
