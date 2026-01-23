import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from articles.models import Article
from users.models import User

@pytest.mark.django_db
def test_user_registration():
    client = APIClient()
    url = reverse('users:user-list-create')
    data = {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'testpass123'
    }
    response = client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['email'] == 'testuser@example.com'
    assert 'token' in response.data

@pytest.mark.django_db
def test_login_returns_jwt():
    user = User.objects.create_user(username='testuser2', email='test2@example.com', password='testpass456')
    client = APIClient()
    url = reverse('users:user-login')
    data = {
        'email': 'test2@example.com',
        'password': 'testpass456'
    }
    response = client.post(url, data, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['email'] == 'test2@example.com'
    assert 'token' in response.data

@pytest.mark.django_db
def test_authenticated_article_creation():
    user = User.objects.create_user(username='author', email='author@example.com', password='authorpass')
    client = APIClient()
    login_url = reverse('users:user-login')
    login_data = {
        'email': 'author@example.com',
        'password': 'authorpass'
    }
    login_response = client.post(login_url, login_data, format='json')
    token = login_response.data['token']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    url = reverse('articles:article-list-create')
    data = {
        'article': {
            'title': 'Test Article',
            'description': 'Test desc',
            'body': 'Test body',
            'tagList': ['django', 'pytest']
        }
    }
    response = client.post(url, data, format='json')
    if response.status_code != status.HTTP_201_CREATED:
        print('DEBUG article creation error:', response.data)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['article']['title'] == 'Test Article'
    assert response.data['article']['author']['username'] == 'author'

@pytest.mark.django_db
def test_permission_enforcement_on_article_edit():
    author = User.objects.create_user(username='author2', email='author2@example.com', password='authorpass2')
    other = User.objects.create_user(username='other', email='other@example.com', password='otherpass')
    article = Article.objects.create(title='A', description='B', body='C', author=author)
    client = APIClient()
    login_url = reverse('users:user-login')
    login_data = {
        'email': 'other@example.com',
        'password': 'otherpass'
    }
    login_response = client.post(login_url, login_data, format='json')
    token = login_response.data['token']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    url = reverse('articles:article-detail', kwargs={'slug': article.slug})
    data = {
        'article': {
            'title': 'Hacked',
            'description': 'Hacked',
            'body': 'Hacked',
            'tagList': []
        }
    }
    response = client.put(url, data, format='json')
    assert response.status_code == status.HTTP_403_FORBIDDEN
