import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from users.models import User
from articles.models import Article

@pytest.mark.django_db
def test_favorite_article_authenticated():
    user = User.objects.create_user(username='alice', email='alice@example.com', password='pw123456')
    article = Article.objects.create(title='A1', description='D1', body='B1', author=user)
    client = APIClient()
    login_url = reverse('users:user-login')
    login_data = {'email': 'alice@example.com', 'password': 'pw123456'}
    login_response = client.post(login_url, login_data, format='json')
    token = login_response.data['token']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    url = reverse('articles:article-favorite', kwargs={'slug': article.slug})
    response = client.post(url)
    assert response.status_code == 200
    assert response.data['article']['favorited'] is True
    assert response.data['article']['favorites_count'] == 1

@pytest.mark.django_db
def test_favorite_idempotent():
    user = User.objects.create_user(username='bob', email='bob@example.com', password='pw123456')
    article = Article.objects.create(title='A2', description='D2', body='B2', author=user)
    client = APIClient()
    login_url = reverse('users:user-login')
    login_data = {'email': 'bob@example.com', 'password': 'pw123456'}
    login_response = client.post(login_url, login_data, format='json')
    token = login_response.data['token']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    url = reverse('articles:article-favorite', kwargs={'slug': article.slug})
    client.post(url)
    response = client.post(url)
    assert response.status_code == 200
    assert response.data['article']['favorited'] is True
    assert response.data['article']['favorites_count'] == 1

@pytest.mark.django_db
def test_unfavorite_article():
    user = User.objects.create_user(username='carol', email='carol@example.com', password='pw123456')
    article = Article.objects.create(title='A3', description='D3', body='B3', author=user)
    client = APIClient()
    login_url = reverse('users:user-login')
    login_data = {'email': 'carol@example.com', 'password': 'pw123456'}
    login_response = client.post(login_url, login_data, format='json')
    token = login_response.data['token']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    url = reverse('articles:article-favorite', kwargs={'slug': article.slug})
    client.post(url)
    response = client.delete(url)
    assert response.status_code == 200
    assert response.data['article']['favorited'] is False
    assert response.data['article']['favorites_count'] == 0

@pytest.mark.django_db
def test_favorite_requires_authentication():
    user = User.objects.create_user(username='dave', email='dave@example.com', password='pw123456')
    article = Article.objects.create(title='A4', description='D4', body='B4', author=user)
    client = APIClient()
    url = reverse('articles:article-favorite', kwargs={'slug': article.slug})
    response = client.post(url)
    assert response.status_code == 401

@pytest.mark.django_db
def test_unfavorite_requires_authentication():
    user = User.objects.create_user(username='eve', email='eve@example.com', password='pw123456')
    article = Article.objects.create(title='A5', description='D5', body='B5', author=user)
    client = APIClient()
    url = reverse('articles:article-favorite', kwargs={'slug': article.slug})
    response = client.delete(url)
    assert response.status_code == 401
