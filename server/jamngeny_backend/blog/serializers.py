#blog/serializers.py
from rest_framework import serializers
from .models import Article, Tag
from accounts.serializers import UserSerializer


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug', 'created_at')
        read_only_fields = ('id', 'slug', 'created_at')


class ArticleListSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    
    class Meta:
        model = Article
        fields = (
            'id', 'title', 'slug', 'author', 'excerpt', 
            'tags', 'read_time', 'featured_image', 'published_at',
            'created_at'
        )
        read_only_fields = ('id', 'slug', 'created_at', 'published_at')


class ArticleDetailSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    
    class Meta:
        model = Article
        fields = (
            'id', 'title', 'slug', 'author', 'excerpt', 'sanitized_content',
            'tags', 'read_time', 'featured_image', 'meta_description',
            'is_published', 'published_at', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'slug', 'created_at', 'updated_at', 'published_at')


class ArticleCreateSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Tag.objects.all(),
        required=False
    )
    
    class Meta:
        model = Article
        fields = (
            'title', 'slug', 'excerpt', 'content', 'tags',
            'read_time', 'featured_image', 'meta_description',
            'is_published'
        )
        extra_kwargs = {
            'slug': {'required': False},
            'read_time': {'required': False},
        }
    
    def create(self, validated_data):
        tags_data = validated_data.pop('tags', [])
        article = Article.objects.create(**validated_data)
        article.tags.set(tags_data)
        return article
    
    def update(self, instance, validated_data):
        tags_data = validated_data.pop('tags', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        
        if tags_data is not None:
            instance.tags.set(tags_data)
        
        return instance