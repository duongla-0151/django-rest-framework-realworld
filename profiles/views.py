"""
Views for profiles app.

Provides API endpoints for user profile management.
Profile endpoints will be implemented in future phases.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.exceptions import NotFound, ValidationError
from .models import Profile
from .serializers import ProfileSerializer

User = get_user_model()

class ProfileFollowAPIView(APIView):
	"""
	POST   /api/profiles/:username/follow   - Follow a user
	DELETE /api/profiles/:username/follow   - Unfollow a user
	Only authenticated users. Cannot follow self. Idempotent. Returns profile.
	"""
	permission_classes = [IsAuthenticated]

	def get_profile(self, username):
		try:
			user = User.objects.get(username=username)
		except User.DoesNotExist:
			raise NotFound('User not found.')
		try:
			return user.profile
		except Profile.DoesNotExist:
			raise NotFound('Profile not found.')

	def post(self, request, username):
		current_profile = request.user.profile
		target_profile = self.get_profile(username)
		if current_profile == target_profile:
			raise ValidationError('You cannot follow yourself.')
		current_profile.follows.add(target_profile)  # Idempotent
		current_profile.save()
		serializer = ProfileSerializer(target_profile, context={'request': request})
		return Response({'profile': serializer.data}, status=status.HTTP_200_OK)

	def delete(self, request, username):
		current_profile = request.user.profile
		target_profile = self.get_profile(username)
		if current_profile == target_profile:
			raise ValidationError('You cannot unfollow yourself.')
		current_profile.follows.remove(target_profile)  # Idempotent
		current_profile.save()
		serializer = ProfileSerializer(target_profile, context={'request': request})
		return Response({'profile': serializer.data}, status=status.HTTP_200_OK)
