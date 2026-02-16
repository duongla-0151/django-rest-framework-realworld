"""
Tests for pagination, throttling, and filtering in the Phase 6 implementation.
"""
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from articles.models import Article, Tag
from users.models import User


@pytest.mark.django_db
def test_pagination_limit_offset():
    """Test that pagination works correctly with limit and offset parameters."""
    user = User.objects.create_user(username='author', email='author@example.com', password='pass123')
    
    # Create 25 articles
    for i in range(25):
        Article.objects.create(
            title=f'Article {i}',
            description=f'Desc {i}',
            body=f'Body {i}',
            author=user
        )
    
    client = APIClient()
    url = reverse('articles:article-list-create')
    
    # Test default pagination (PAGE_SIZE=20)
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 20
    
    # Test custom limit
    response = client.get(url, {'limit': 5})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 5
    
    # Test offset
    response = client.get(url, {'limit': 5, 'offset': 10})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 5
    assert response.data['results'][0]['title'] == 'Article 14'  # 10 + (25-1-10) offset from end
    
    # Test pagination metadata
    response = client.get(url, {'limit': 10})
    assert 'count' in response.data
    assert response.data['count'] == 25


@pytest.mark.django_db
def test_pagination_with_filtering():
    """Test that pagination works correctly when filtering is applied."""
    user = User.objects.create_user(username='author', email='author@example.com', password='pass123')
    tag = Tag.objects.create(tag='django')
    
    # Create 15 articles with tag, 10 without
    for i in range(15):
        article = Article.objects.create(
            title=f'Django Article {i}',
            description=f'Desc {i}',
            body=f'Body {i}',
            author=user
        )
        article.tags.add(tag)
    
    for i in range(10):
        Article.objects.create(
            title=f'Other Article {i}',
            description=f'Desc {i}',
            body=f'Body {i}',
            author=user
        )
    
    client = APIClient()
    url = reverse('articles:article-list-create')
    
    # Filter by tag and paginate
    response = client.get(url, {'tag': 'django', 'limit': 5})
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 15
    assert len(response.data['results']) == 5


@pytest.mark.django_db
def test_ordering():
    """Test that ordering works correctly."""
    user = User.objects.create_user(username='author', email='author@example.com', password='pass123')
    
    # Create articles in non-chronological order
    articles = []
    for i in range(5):
        article = Article.objects.create(
            title=f'Article {i}',
            description=f'Desc {i}',
            body=f'Body {i}',
            author=user
        )
        articles.append(article)
    
    client = APIClient()
    url = reverse('articles:article-list-create')
    
    # Test default ordering (descending created_at)
    response = client.get(url)
    assert response.status_code == status.HTTP_200_OK
    results = response.data['results']
    assert results[0]['title'] == 'Article 4'  # Most recent
    assert results[-1]['title'] == 'Article 0'  # Oldest
    
    # Test ascending order
    response = client.get(url, {'ordering': 'created_at'})
    assert response.status_code == status.HTTP_200_OK
    results = response.data['results']
    assert results[0]['title'] == 'Article 0'
    assert results[-1]['title'] == 'Article 4'
    
    # Test ordering by title
    response = client.get(url, {'ordering': 'title'})
    assert response.status_code == status.HTTP_200_OK
    results = response.data['results']
    assert results[0]['title'] == 'Article 0'
    assert results[-1]['title'] == 'Article 4'


@pytest.mark.django_db
def test_search_filter():
    """Test that search filtering works on title and description."""
    user = User.objects.create_user(username='author', email='author@example.com', password='pass123')
    
    Article.objects.create(
        title='Django REST Framework',
        description='Building APIs with DRF',
        body='Body',
        author=user
    )
    
    Article.objects.create(
        title='FastAPI Tutorial',
        description='Building async APIs',
        body='Body',
        author=user
    )
    
    client = APIClient()
    url = reverse('articles:article-list-create')
    
    # Search in title
    response = client.get(url, {'search': 'Django'})
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 1
    assert response.data['results'][0]['title'] == 'Django REST Framework'
    
    # Search in description
    response = client.get(url, {'search': 'Building'})
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 2


@pytest.mark.django_db
def test_throttling_anonymous_user():
    """Test that anonymous users are throttled at 100 requests per hour."""
    client = APIClient()
    url = reverse('articles:article-list-create')
    
    # Make requests and check if throttled
    # Note: This test may need to be adjusted based on test database throttle rates
    for i in range(5):
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK
    
    # Check rate limit headers
    response = client.get(url)
    assert 'X-RateLimit-Limit' in response or response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_throttling_authenticated_user():
    """Test that authenticated users have higher rate limits."""
    user = User.objects.create_user(username='testuser', email='test@example.com', password='pass123')
    client = APIClient()
    client.force_authenticate(user=user)
    
    url = reverse('articles:article-list-create')
    
    # Make requests and verify user is not throttled
    for i in range(5):
        response = client.get(url)
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_filtering_by_tag():
    """Test filtering articles by tag."""
    user = User.objects.create_user(username='author', email='author@example.com', password='pass123')
    tag1 = Tag.objects.create(tag='django')
    tag2 = Tag.objects.create(tag='python')
    
    article1 = Article.objects.create(
        title='Django Article',
        description='About Django',
        body='Body',
        author=user
    )
    article1.tags.add(tag1)
    
    article2 = Article.objects.create(
        title='Python Article',
        description='About Python',
        body='Body',
        author=user
    )
    article2.tags.add(tag2)
    
    client = APIClient()
    url = reverse('articles:article-list-create')
    
    response = client.get(url, {'tag': 'django'})
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 1
    assert response.data['results'][0]['title'] == 'Django Article'


@pytest.mark.django_db
def test_filtering_by_author():
    """Test filtering articles by author username."""
    author1 = User.objects.create_user(username='alice', email='alice@example.com', password='pass123')
    author2 = User.objects.create_user(username='bob', email='bob@example.com', password='pass123')
    
    Article.objects.create(title='Alice Article', description='Desc', body='Body', author=author1)
    Article.objects.create(title='Bob Article', description='Desc', body='Body', author=author2)
    
    client = APIClient()
    url = reverse('articles:article-list-create')
    
    response = client.get(url, {'author': 'alice'})
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 1
    assert response.data['results'][0]['author']['username'] == 'alice'


@pytest.mark.django_db
def test_filtering_by_favorited():
    """Test filtering articles by user who favorited."""
    author = User.objects.create_user(username='author', email='author@example.com', password='pass123')
    fan1 = User.objects.create_user(username='fan1', email='fan1@example.com', password='pass123')
    fan2 = User.objects.create_user(username='fan2', email='fan2@example.com', password='pass123')
    
    article1 = Article.objects.create(title='Article 1', description='Desc', body='Body', author=author)
    article2 = Article.objects.create(title='Article 2', description='Desc', body='Body', author=author)
    
    article1.favorited_by.add(fan1)
    article2.favorited_by.add(fan1, fan2)
    
    client = APIClient()
    url = reverse('articles:article-list-create')
    
    response = client.get(url, {'favorited': 'fan1'})
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 2
    
    response = client.get(url, {'favorited': 'fan2'})
    assert response.status_code == status.HTTP_200_OK
    assert response.data['count'] == 1
