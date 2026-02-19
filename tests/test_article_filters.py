import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from users.models import User
from articles.models import Article, Tag

@pytest.mark.django_db
def test_article_filter_by_tag():
    user = User.objects.create_user(username='alice', email='alice@example.com', password='pw123456')
    tag1 = Tag.objects.create(tag='django')
    tag2 = Tag.objects.create(tag='pytest')
    a1 = Article.objects.create(title='A1', description='D1', body='B1', author=user)
    a2 = Article.objects.create(title='A2', description='D2', body='B2', author=user)
    a1.tags.add(tag1)
    a2.tags.add(tag2)
    client = APIClient()
    url = reverse('articles:article-list-create')
    response = client.get(url, {'tag': 'django'})
    assert response.status_code == 200
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['title'] == 'A1'

@pytest.mark.django_db
def test_article_filter_by_author():
    alice = User.objects.create_user(username='alice', email='alice@example.com', password='pw123456')
    bob = User.objects.create_user(username='bob', email='bob@example.com', password='pw123456')
    a1 = Article.objects.create(title='A1', description='D1', body='B1', author=alice)
    a2 = Article.objects.create(title='A2', description='D2', body='B2', author=bob)
    client = APIClient()
    url = reverse('articles:article-list-create')
    response = client.get(url, {'author': 'bob'})
    assert response.status_code == 200
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['author']['username'] == 'bob'

@pytest.mark.django_db
def test_article_filter_by_favorited():
    alice = User.objects.create_user(username='alice', email='alice@example.com', password='pw123456')
    bob = User.objects.create_user(username='bob', email='bob@example.com', password='pw123456')
    article = Article.objects.create(title='A1', description='D1', body='B1', author=alice)
    article.favorited_by.add(bob)
    client = APIClient()
    url = reverse('articles:article-list-create')
    response = client.get(url, {'favorited': 'bob'})
    assert response.status_code == 200
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['title'] == 'A1'

@pytest.mark.django_db
def test_article_filter_combined():
    alice = User.objects.create_user(username='alice', email='alice@example.com', password='pw123456')
    tag = Tag.objects.create(tag='django')
    article = Article.objects.create(title='A1', description='D1', body='B1', author=alice)
    article.tags.add(tag)
    article.favorited_by.add(alice)
    client = APIClient()
    url = reverse('articles:article-list-create')
    response = client.get(url, {'tag': 'django', 'author': 'alice', 'favorited': 'alice'})
    assert response.status_code == 200
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['title'] == 'A1'
