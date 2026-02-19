import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from users.models import User
from profiles.models import Profile

@pytest.mark.django_db
def test_follow_success():
    alice = User.objects.create_user(username='alice', email='alice@example.com', password='pw123456')
    bob = User.objects.create_user(username='bob', email='bob@example.com', password='pw123456')
    # Ensure profiles exist
    alice_profile = Profile.objects.get(user=alice)
    bob_profile = Profile.objects.get(user=bob)
    
    client = APIClient()
    login_url = reverse('users:user-login')
    login_data = {'email': 'alice@example.com', 'password': 'pw123456'}
    login_response = client.post(login_url, login_data, format='json')
    token = login_response.data['token']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    url = reverse('profiles:profile-follow', kwargs={'username': 'bob'})
    response = client.post(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['profile']['username'] == 'bob'
    assert response.data['profile']['following'] is True

@pytest.mark.django_db
def test_unfollow_success():
    alice = User.objects.create_user(username='alice', email='alice@example.com', password='pw123456')
    bob = User.objects.create_user(username='bob', email='bob@example.com', password='pw123456')
    # Ensure profiles exist
    alice_profile = Profile.objects.get(user=alice)
    bob_profile = Profile.objects.get(user=bob)
    
    client = APIClient()
    login_url = reverse('users:user-login')
    login_data = {'email': 'alice@example.com', 'password': 'pw123456'}
    login_response = client.post(login_url, login_data, format='json')
    token = login_response.data['token']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    url = reverse('profiles:profile-follow', kwargs={'username': 'bob'})
    client.post(url)
    response = client.delete(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['profile']['username'] == 'bob'
    assert response.data['profile']['following'] is False

@pytest.mark.django_db
def test_follow_idempotent():
    alice = User.objects.create_user(username='alice', email='alice@example.com', password='pw123456')
    bob = User.objects.create_user(username='bob', email='bob@example.com', password='pw123456')
    # Ensure profiles exist
    alice_profile = Profile.objects.get(user=alice)
    bob_profile = Profile.objects.get(user=bob)
    
    client = APIClient()
    login_url = reverse('users:user-login')
    login_data = {'email': 'alice@example.com', 'password': 'pw123456'}
    login_response = client.post(login_url, login_data, format='json')
    token = login_response.data['token']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    url = reverse('profiles:profile-follow', kwargs={'username': 'bob'})
    client.post(url)
    response = client.post(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['profile']['following'] is True

@pytest.mark.django_db
def test_cannot_follow_self():
    alice = User.objects.create_user(username='alice', email='alice@example.com', password='pw123456')
    # Ensure profile exists
    alice_profile = Profile.objects.get(user=alice)
    
    client = APIClient()
    login_url = reverse('users:user-login')
    login_data = {'email': 'alice@example.com', 'password': 'pw123456'}
    login_response = client.post(login_url, login_data, format='json')
    token = login_response.data['token']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    url = reverse('profiles:profile-follow', kwargs={'username': 'alice'})
    response = client.post(url)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'cannot follow yourself' in str(response.data).lower()

@pytest.mark.django_db
def test_follow_requires_authentication():
    alice = User.objects.create_user(username='alice', email='alice@example.com', password='pw123456')
    # Ensure profile exists
    alice_profile = Profile.objects.get(user=alice)
    
    url = reverse('profiles:profile-follow', kwargs={'username': 'alice'})
    client = APIClient()
    response = client.post(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
