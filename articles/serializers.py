"""
Serializers for articles app.
"""
from rest_framework import serializers


from .models import Article, Tag, Comment
from users.serializers import UserSerializer
from constants import ARTICLE_TITLE_MAX_LENGTH, ARTICLE_TAG_MAX_LENGTH, ARTICLE_DESCRIPTION_DEFAULT



class TagSerializer(serializers.ModelSerializer):
    """
    Serializer for Tag model.
    """
    class Meta:
        model = Tag
        fields = ['tag']


class ArticleSerializer(serializers.ModelSerializer):
    """
    Serializer for Article model.

    Includes nested author information and tag list.
    """
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    tag_list = serializers.ListField(
        child=serializers.CharField(max_length=64),
        write_only=True,
        required=False,
        default=[]
    )
    favorites_count = serializers.SerializerMethodField()
    favorited = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'slug',
            'title',
            'description',
            'body',
            'tags',
            'tag_list',
            'created_at',
            'updated_at',
            'favorites_count',
            'favorited',
            'author',
        ]
        read_only_fields = ['slug', 'created_at', 'updated_at', 'author']

    def get_favorites_count(self, obj):
        """Return the number of users who favorited this article."""
        return obj.favorited_by.count()

    def get_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.favorited_by.filter(pk=request.user.pk).exists()
        return False

    def create(self, validated_data):
        """Create article with tags."""
        tag_list = validated_data.pop('tag_list', [])

        # Remove 'request' if present (should not be, but for safety)
        validated_data.pop('request', None)

        # Get author from context (set in view)
        request = self.context.get('request')
        author = None
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            author = request.user

        article = Article.objects.create(author=author, **validated_data)

        # Create or get tags and associate with article
        for tag_name in tag_list:
            tag, _ = Tag.objects.get_or_create(tag=tag_name)
            article.tags.add(tag)

        return article

    def update(self, instance, validated_data):
        """Update article with optional tag updates."""
        tag_list = validated_data.pop('tag_list', None)

        # Update article fields
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        # Update tags if provided
        if tag_list is not None:
            instance.tags.clear()
            for tag_name in tag_list:
                tag, _ = Tag.objects.get_or_create(tag=tag_name)
                instance.tags.add(tag)

        return instance


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for Comment model.

    Note: Comment endpoints will be implemented in a future phase.
    """
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = [
            'id',
            'body',
            'created_at',
            'updated_at',
            'author',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'author']
