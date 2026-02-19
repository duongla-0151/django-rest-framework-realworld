"""
URL configuration for articles app.

Endpoints:
    /api/articles       - List/create articles
    /api/articles/:slug - Retrieve/update/delete article
    /api/tags           - List all tags
"""
from django.urls import path


from . import views

app_name = 'articles'

urlpatterns = [
    # Articles
    path('articles/', views.ArticleListCreateAPIView.as_view(), name='article-list-create'),
    path('articles/<slug:slug>/', views.ArticleRetrieveUpdateDestroyAPIView.as_view(), name='article-detail'),
    path('articles/<slug:slug>/favorite', views.ArticleFavoriteAPIView.as_view(), name='article-favorite'),

    # Tags
    path('tags/', views.TagListAPIView.as_view(), name='tag-list'),
]
