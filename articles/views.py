"""
Views for articles app.

Provides API endpoints for articles and tags management.
"""
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.exceptions import NotFound
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .permissions import IsAuthorOrReadOnly, IsCommentAuthor

from .models import Article, Tag, Comment
from .serializers import ArticleSerializer, TagSerializer, CommentSerializer
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


class ArticleFavoriteAPIView(APIView):
    """
    POST   /api/articles/:slug/favorite   - Favorite an article
    DELETE /api/articles/:slug/favorite   - Unfavorite an article
    Only authenticated users. Idempotent. Returns updated article.
    """
    permission_classes = [IsAuthenticated]

    def get_article(self, slug):
        try:
            return Article.objects.select_related('author').prefetch_related('tags', 'favorited_by').get(slug=slug)
        except Article.DoesNotExist:
            raise NotFound('Article not found.')

    def post(self, request, slug):
        article = self.get_article(slug)
        user = request.user
        article.favorited_by.add(user)  # Idempotent
        article.save()
        serializer = ArticleSerializer(article, context={'request': request})
        return Response({'article': serializer.data}, status=status.HTTP_200_OK)

    def delete(self, request, slug):
        article = self.get_article(slug)
        user = request.user
        article.favorited_by.remove(user)  # Idempotent
        article.save()
        serializer = ArticleSerializer(article, context={'request': request})
        return Response({'article': serializer.data}, status=status.HTTP_200_OK)


class CommentListCreateAPIView(generics.ListCreateAPIView):
    """
    GET  /api/articles/:slug/comments  - List all comments for an article
    POST /api/articles/:slug/comments  - Create a new comment
    
    Permissions:
    - Anonymous users can read (GET)
    - Only authenticated users can create (POST)
    """
    serializer_class = CommentSerializer
    lookup_field = 'slug'
    pagination_class = None  # Comments don't need pagination
    ordering = ['-created_at']

    def get_article(self):
        """Get article by slug from URL kwargs."""
        slug = self.kwargs.get('slug')
        try:
            return Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            raise NotFound({'detail': 'Article not found.'})

    def get_queryset(self):
        """Get comments for the article."""
        article = self.get_article()
        return article.comments.select_related('author').all()

    def get_permissions(self):
        """Anonymous can read, only authenticated can create."""
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [AllowAny()]

    def perform_create(self, serializer):
        """Create comment with author from request.user and article from URL."""
        article = self.get_article()
        serializer.save(author=self.request.user, article=article)


class CommentDestroyAPIView(generics.DestroyAPIView):
    """
    DELETE /api/articles/:slug/comments/:id  - Delete a comment
    
    Permissions:
    - Only comment author can delete
    - Non-author → 403
    - Anonymous → 401
    """
    serializer_class = CommentSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'comment_id'
    permission_classes = [IsCommentAuthor]

    def get_article(self):
        """Get article by slug from URL kwargs."""
        slug = self.kwargs.get('slug')
        try:
            return Article.objects.get(slug=slug)
        except Article.DoesNotExist:
            raise NotFound({'detail': 'Article not found.'})

    def get_queryset(self):
        """Get comments for the article."""
        article = self.get_article()
        return article.comments.all()

    def delete(self, request, *args, **kwargs):
        """Delete comment and return 204 No Content."""
        response = super().delete(request, *args, **kwargs)
        return Response(status=status.HTTP_204_NO_CONTENT)
