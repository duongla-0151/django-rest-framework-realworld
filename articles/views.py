"""
Views for articles app.

Provides API endpoints for articles and tags management.
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import IsAuthorOrReadOnly

from .models import Article, Tag
from .serializers import ArticleSerializer, TagSerializer


class ArticleListCreateAPIView(generics.ListCreateAPIView):
    """
    GET  /api/articles/  - List all articles (with filtering)
    POST /api/articles/  - Create a new article
    """

    serializer_class = ArticleSerializer
    lookup_field = 'slug'
    filterset_fields = []  # Not used, custom filtering below

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_queryset(self):
        return self.get_filtered_queryset()

    def get_filtered_queryset(self):
        qs = Article.objects.select_related('author').prefetch_related('tags', 'favorited_by').all()
        tag = self.request.query_params.get('tag')
        author = self.request.query_params.get('author')
        favorited = self.request.query_params.get('favorited')
        if tag:
            qs = qs.filter(tags__tag=tag)
        if author:
            qs = qs.filter(author__username=author)
        if favorited:
            qs = qs.filter(favorited_by__username=favorited)
        return qs.distinct()

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
    GET /api/tags/  - List all tags
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None  # Tags don't need pagination
