from rest_framework import serializers
from django.conf import settings
from .models import PortfolioCategory, PortfolioItem, PortfolioImage


class PortfolioImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = PortfolioImage
        fields = ('id', 'image_url', 'caption', 'alt_text', 'order', 'is_featured')
        read_only_fields = ('id',)

    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            # Fallback to BASE_URL if no request context
            return f"{settings.BASE_URL}{obj.image.url}"
        return None


class PortfolioCategorySerializer(serializers.ModelSerializer):
    item_count = serializers.SerializerMethodField()

    class Meta:
        model = PortfolioCategory
        fields = ('id', 'name', 'slug', 'description', 'order', 'item_count', 'created_at')
        read_only_fields = ('id', 'slug', 'created_at')

    def get_item_count(self, obj):
        return obj.portfolio_items.filter(is_published=True).count()


class PortfolioItemListSerializer(serializers.ModelSerializer):
    category = PortfolioCategorySerializer(read_only=True)
    featured_image_url = serializers.SerializerMethodField()
    technologies = serializers.ListField(child=serializers.CharField(), required=False)

    class Meta:
        model = PortfolioItem
        fields = (
            'id', 'title', 'slug', 'category', 'summary', 
            'featured_image_url', 'client', 'project_date', 'duration',
            'technologies', 'link', 'is_featured', 'created_at'
        )
        read_only_fields = ('id', 'slug', 'created_at')

    def get_featured_image_url(self, obj):
        if obj.featured_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.featured_image.url)
            # Fallback to BASE_URL if no request context
            return f"{settings.BASE_URL}{obj.featured_image.url}"
        return None


class PortfolioItemDetailSerializer(serializers.ModelSerializer):
    category = PortfolioCategorySerializer(read_only=True)
    secondary_categories = PortfolioCategorySerializer(many=True, read_only=True)
    images = serializers.SerializerMethodField()
    featured_image_url = serializers.SerializerMethodField()
    technologies = serializers.ListField(child=serializers.CharField(), required=False)
    display_date = serializers.ReadOnlyField()

    class Meta:
        model = PortfolioItem
        fields = (
            'id', 'title', 'slug', 'category', 'secondary_categories',
            'summary', 'sanitized_content', 'featured_image_url', 'images',
            'client', 'project_date', 'display_date', 'duration', 'link',
            'technologies', 'meta_description', 'is_featured', 'metadata',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'slug', 'created_at', 'updated_at')

    def get_featured_image_url(self, obj):
        if obj.featured_image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.featured_image.url)
            return f"{settings.BASE_URL}{obj.featured_image.url}"
        return None

    def get_images(self, obj):
        images = obj.images.all().order_by('order')
        return PortfolioImageSerializer(images, many=True, context=self.context).data


class PortfolioItemCreateSerializer(serializers.ModelSerializer):
    secondary_categories = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=PortfolioCategory.objects.filter(is_active=True),
        required=False
    )
    technologies = serializers.ListField(child=serializers.CharField(), required=False)

    class Meta:
        model = PortfolioItem
        fields = (
            'title', 'slug', 'category', 'secondary_categories', 'summary', 'content',
            'featured_image', 'client', 'project_date', 'duration', 'link',
            'technologies', 'meta_description', 'is_published', 'is_featured', 'metadata'
        )
        extra_kwargs = {
            'slug': {'required': False},
        }

    def create(self, validated_data):
        secondary_categories_data = validated_data.pop('secondary_categories', [])
        portfolio_item = PortfolioItem.objects.create(**validated_data)
        portfolio_item.secondary_categories.set(secondary_categories_data)
        return portfolio_item

    def update(self, instance, validated_data):
        secondary_categories_data = validated_data.pop('secondary_categories', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        
        if secondary_categories_data is not None:
            instance.secondary_categories.set(secondary_categories_data)
        
        return instance