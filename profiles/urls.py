"""
URL configuration for profiles app.

Endpoints:
    /api/profiles/:username - Get user profile (future implementation)
"""
from django.urls import path

from . import views

app_name = 'profiles'

urlpatterns = [
    path('profiles/<str:username>/follow', views.ProfileFollowAPIView.as_view(), name='profile-follow'),
]
