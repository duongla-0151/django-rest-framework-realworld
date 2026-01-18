"""
Article, Tag, and Comment models for the conduit application.
"""

from django.conf import settings
from django.db import models
from django.utils.text import slugify
import uuid
from constants import ARTICLE_TITLE_MAX_LENGTH, ARTICLE_TAG_MAX_LENGTH, ARTICLE_DESCRIPTION_DEFAULT



class Tag(models.Model):
    """
    Tag model for categorizing articles.
    """
    tag = models.CharField(max_length=ARTICLE_TAG_MAX_LENGTH, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tags'
        ordering = ['tag']

    def __str__(self):
        return self.tag



class Article(models.Model):
    """
    Article model representing blog posts.
    Uses a custom slug generation with slugify + UUID suffix for uniqueness.
    """
    slug = models.SlugField(max_length=ARTICLE_TITLE_MAX_LENGTH, unique=True, db_index=True)
    title = models.CharField(max_length=ARTICLE_TITLE_MAX_LENGTH)
    description = models.TextField(blank=True, default=ARTICLE_DESCRIPTION_DEFAULT)
    body = models.TextField()

    # Relationships
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='articles',
        null=True,
        blank=True
    )
    tags = models.ManyToManyField(Tag, related_name='articles', blank=True)
    favorited_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='favorite_articles',
        blank=True
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'articles'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Generate unique slug from title if not provided."""
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)

    def _generate_unique_slug(self):
        """
        Generate a unique slug using slugify + short UUID suffix.
        Example: 'my-article-title-a1b2c3d4'
        """
        base_slug = slugify(self.title)
        unique_suffix = uuid.uuid4().hex[:8]
        return f"{base_slug}-{unique_suffix}"



class Comment(models.Model):
    """
    Comment model for article comments.
    Note: Comment API endpoints will be implemented in a future phase,
    but the model is defined here for relationship completeness.
    """
    body = models.TextField()

    # Relationships
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='comments',
        null=True,
        blank=True
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'comments'
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.author} on {self.article}"
