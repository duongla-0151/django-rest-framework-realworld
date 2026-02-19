"""
Filter sets for articles app.
"""
import django_filters
from .models import Article


class ArticleFilterSet(django_filters.FilterSet):
    """
    FilterSet for Article model.

    Supports filtering by:
    - tag: Filter articles by tag name
    - author: Filter articles by author username
    - favorited: Filter articles favorited by a specific user
    """
    tag = django_filters.CharFilter(
        field_name='tags__tag',
        lookup_expr='iexact',
        label='Filter by tag'
    )
    author = django_filters.CharFilter(
        field_name='author__username',
        lookup_expr='iexact',
        label='Filter by author username'
    )
    favorited = django_filters.CharFilter(
        field_name='favorited_by__username',
        lookup_expr='iexact',
        label='Filter by user who favorited'
    )

    class Meta:
        model = Article
        fields = ['tag', 'author', 'favorited']
