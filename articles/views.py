"""
Views for articles app.

Provides API endpoints for articles and tags management.
"""
from rest_framework import generics, status
from rest_framework.response import Response

from .models import Article, Tag
from .serializers import ArticleSerializer, TagSerializer


class ArticleListCreateAPIView(generics.ListCreateAPIView):
    """
    GET  /api/articles/  - List all articles (with filtering)
    POST /api/articles/  - Create a new article
    """
    serializer_class = ArticleSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        return Article.objects.select_related('author').prefetch_related('tags', 'favorited_by').all()


class ArticleRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/articles/:slug/  - Retrieve article by slug
    PUT    /api/articles/:slug/  - Update article
    PATCH  /api/articles/:slug/  - Partial update article
    DELETE /api/articles/:slug/  - Delete article
    """
    serializer_class = ArticleSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        return Article.objects.select_related('author').prefetch_related('tags', 'favorited_by').all()


class TagListAPIView(generics.ListAPIView):
    """
    GET /api/tags/  - List all tags
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None  # Tags don't need pagination
