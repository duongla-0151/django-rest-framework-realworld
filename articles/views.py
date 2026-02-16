"""
Views for articles app.

Provides API endpoints for articles and tags management.
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .permissions import IsAuthorOrReadOnly

from .models import Article, Tag
from .serializers import ArticleSerializer, TagSerializer
from .filterset import ArticleFilterSet


class ArticleListCreateAPIView(generics.ListCreateAPIView):
    """
    GET  /api/articles/  - List all articles (with filtering, pagination, ordering)
    POST /api/articles/  - Create a new article
    
    Filtering:
    - tag: Filter by tag name (e.g., ?tag=django)
    - author: Filter by author username (e.g., ?author=john)
    - favorited: Filter by user who favorited (e.g., ?favorited=john)
    
    Searching:
    - search: Search in title and description (e.g., ?search=keyword)
    
    Ordering:
    - ordering: Order by field (e.g., ?ordering=-created_at or ?ordering=title)
    
    Pagination:
    - limit: Number of articles per page (default 20)
    - offset: Starting position (e.g., ?limit=5&offset=10)
    """

    serializer_class = ArticleSerializer
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ArticleFilterSet
    search_fields = ['title', 'description', 'body']
    ordering_fields = ['created_at', 'updated_at', 'title']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_queryset(self):
        return Article.objects.select_related('author').prefetch_related('tags', 'favorited_by').all()

    def create(self, request, *args, **kwargs):
        # Accept nested 'article' payload as per RealWorld spec
        article_data = request.data.get('article', {})
        serializer = self.get_serializer(data=article_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        # Return response in RealWorld format
        return Response({'article': serializer.data}, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(request=self.request)


class ArticleRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/articles/:slug/  - Retrieve article by slug
    PUT    /api/articles/:slug/  - Update article
    PATCH  /api/articles/:slug/  - Partial update article
    DELETE /api/articles/:slug/  - Delete article
    """
    serializer_class = ArticleSerializer
    lookup_field = 'slug'
    permission_classes = [IsAuthorOrReadOnly]

    def get_queryset(self):
        return Article.objects.select_related('author').prefetch_related('tags', 'favorited_by').all()


class TagListAPIView(generics.ListAPIView):
    """
    GET /api/tags/  - List all tags (with pagination optionally disabled)
    
    Note: Pagination is disabled by default for tags, but can be included
    by setting pagination_class in the view or via query parameters.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None  # Tags don't need pagination by default
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['tag']
    ordering_fields = ['tag']
    ordering = ['tag']
