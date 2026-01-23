"""
URL configuration for users app.

Endpoints:
    /api/users      - User registration and listing
    /api/user       - Current user retrieval/update (future auth)
"""
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('users/', views.UserListCreateAPIView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', views.UserRetrieveUpdateAPIView.as_view(), name='user-detail'),
]
