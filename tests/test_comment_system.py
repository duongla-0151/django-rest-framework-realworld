"""
Integration tests for comment system (SUB-PHASE 3).
"""
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from articles.models import Article, Comment
from users.models import User


@pytest.mark.django_db
def test_authenticated_user_can_comment():
    """Test that authenticated users can create comments on articles."""
    author = User.objects.create_user(username='author', email='author@example.com', password='pass123')
    commenter = User.objects.create_user(username='commenter', email='commenter@example.com', password='pass123')
    
    article = Article.objects.create(
        title='Test Article',
        description='Test Description',
        body='Test Body',
        author=author
    )
    
    client = APIClient()
    # Login as commenter
    login_url = reverse('users:user-login')
    login_response = client.post(login_url, {'email': 'commenter@example.com', 'password': 'pass123'}, format='json')
    token = login_response.data['token']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    
    # Create comment
    url = reverse('articles:comment-list-create', kwargs={'slug': article.slug})
    comment_data = {'body': 'Great article!'}
    response = client.post(url, comment_data, format='json')
    
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['body'] == 'Great article!'
    assert response.data['author']['username'] == 'commenter'


@pytest.mark.django_db
def test_anonymous_cannot_comment():
    """Test that anonymous users cannot create comments."""
    author = User.objects.create_user(username='author', email='author@example.com', password='pass123')
    
    article = Article.objects.create(
        title='Test Article',
        description='Test Description',
        body='Test Body',
        author=author
    )
    
    client = APIClient()
    url = reverse('articles:comment-list-create', kwargs={'slug': article.slug})
    comment_data = {'body': 'Great article!'}
    response = client.post(url, comment_data, format='json')
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_anonymous_can_read_comments():
    """Test that anonymous users can read comments."""
    author = User.objects.create_user(username='author', email='author@example.com', password='pass123')
    commenter = User.objects.create_user(username='commenter', email='commenter@example.com', password='pass123')
    
    article = Article.objects.create(
        title='Test Article',
        description='Test Description',
        body='Test Body',
        author=author
    )
    
    comment = Comment.objects.create(
        body='Nice article!',
        article=article,
        author=commenter
    )
    
    client = APIClient()
    url = reverse('articles:comment-list-create', kwargs={'slug': article.slug})
    response = client.get(url)
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1  # No pagination
    assert response.data[0]['body'] == 'Nice article!'


@pytest.mark.django_db
def test_comment_author_can_delete():
    """Test that comment author can delete their own comment."""
    author = User.objects.create_user(username='author', email='author@example.com', password='pass123')
    commenter = User.objects.create_user(username='commenter', email='commenter@example.com', password='pass123')
    
    article = Article.objects.create(
        title='Test Article',
        description='Test Description',
        body='Test Body',
        author=author
    )
    
    comment = Comment.objects.create(
        body='Nice article!',
        article=article,
        author=commenter
    )
    
    client = APIClient()
    # Login as commenter
    login_url = reverse('users:user-login')
    login_response = client.post(login_url, {'email': 'commenter@example.com', 'password': 'pass123'}, format='json')
    token = login_response.data['token']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    
    # Delete comment
    url = reverse('articles:comment-delete', kwargs={'slug': article.slug, 'comment_id': comment.id})
    response = client.delete(url)
    
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert not Comment.objects.filter(id=comment.id).exists()


@pytest.mark.django_db
def test_non_author_cannot_delete_comment():
    """Test that non-author cannot delete another's comment (403)."""
    author = User.objects.create_user(username='author', email='author@example.com', password='pass123')
    commenter = User.objects.create_user(username='commenter', email='commenter@example.com', password='pass123')
    other_user = User.objects.create_user(username='other', email='other@example.com', password='pass123')
    
    article = Article.objects.create(
        title='Test Article',
        description='Test Description',
        body='Test Body',
        author=author
    )
    
    comment = Comment.objects.create(
        body='Nice article!',
        article=article,
        author=commenter
    )
    
    client = APIClient()
    # Login as other_user
    login_url = reverse('users:user-login')
    login_response = client.post(login_url, {'email': 'other@example.com', 'password': 'pass123'}, format='json')
    token = login_response.data['token']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    
    # Try to delete comment
    url = reverse('articles:comment-delete', kwargs={'slug': article.slug, 'comment_id': comment.id})
    response = client.delete(url)
    
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert Comment.objects.filter(id=comment.id).exists()  # Comment still exists


@pytest.mark.django_db
def test_anonymous_cannot_delete_comment():
    """Test that anonymous users cannot delete comments (401)."""
    author = User.objects.create_user(username='author', email='author@example.com', password='pass123')
    commenter = User.objects.create_user(username='commenter', email='commenter@example.com', password='pass123')
    
    article = Article.objects.create(
        title='Test Article',
        description='Test Description',
        body='Test Body',
        author=author
    )
    
    comment = Comment.objects.create(
        body='Nice article!',
        article=article,
        author=commenter
    )
    
    client = APIClient()
    url = reverse('articles:comment-delete', kwargs={'slug': article.slug, 'comment_id': comment.id})
    response = client.delete(url)
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert Comment.objects.filter(id=comment.id).exists()  # Comment still exists


@pytest.mark.django_db
def test_invalid_article_slug_returns_404():
    """Test that invalid article slug returns 404."""
    client = APIClient()
    url = reverse('articles:comment-list-create', kwargs={'slug': 'invalid-slug-xyz'})
    response = client.get(url)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_invalid_comment_id_returns_404():
    """Test that invalid comment id returns 404."""
    author = User.objects.create_user(username='author', email='author@example.com', password='pass123')
    
    article = Article.objects.create(
        title='Test Article',
        description='Test Description',
        body='Test Body',
        author=author
    )
    
    client = APIClient()
    # Login as author
    login_url = reverse('users:user-login')
    login_response = client.post(login_url, {'email': 'author@example.com', 'password': 'pass123'}, format='json')
    token = login_response.data['token']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    
    # Try to delete non-existent comment
    url = reverse('articles:comment-delete', kwargs={'slug': article.slug, 'comment_id': 99999})
    response = client.delete(url)
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_comments_ordered_by_created_at_descending():
    """Test that comments are returned ordered by created_at descending."""
    author = User.objects.create_user(username='author', email='author@example.com', password='pass123')
    commenter = User.objects.create_user(username='commenter', email='commenter@example.com', password='pass123')
    
    article = Article.objects.create(
        title='Test Article',
        description='Test Description',
        body='Test Body',
        author=author
    )
    
    # Create multiple comments
    comment1 = Comment.objects.create(body='First comment', article=article, author=commenter)
    comment2 = Comment.objects.create(body='Second comment', article=article, author=commenter)
    comment3 = Comment.objects.create(body='Third comment', article=article, author=commenter)
    
    client = APIClient()
    url = reverse('articles:comment-list-create', kwargs={'slug': article.slug})
    response = client.get(url)
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 3
    # Should be in reverse order (newest first)
    assert response.data[0]['body'] == 'Third comment'
    assert response.data[1]['body'] == 'Second comment'
    assert response.data[2]['body'] == 'First comment'
