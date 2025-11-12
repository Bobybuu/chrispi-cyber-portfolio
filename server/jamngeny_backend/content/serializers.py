from rest_framework import serializers
from .models import About, Service


class AboutSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()
    profile_pdf_url = serializers.SerializerMethodField()
    social_links = serializers.DictField(child=serializers.URLField(), required=False)

    class Meta:
        model = About
        fields = (
            'id', 'name', 'title', 'sanitized_bio', 
            'photo_url', 'profile_pdf_url', 'email', 'phone', 'location',
            'social_links', 'experience_years', 'projects_completed', 'clients_served',
            'meta_title', 'meta_description', 'updated_at'
        )
        read_only_fields = ('id', 'updated_at')

    def get_photo_url(self, obj):
        if obj.photo:
            return obj.photo.url
        return None

    def get_profile_pdf_url(self, obj):
        if obj.profile_pdf:
            return obj.profile_pdf.url
        return None


class AboutUpdateSerializer(serializers.ModelSerializer):
    social_links = serializers.DictField(child=serializers.URLField(), required=False)

    class Meta:
        model = About
        fields = (
            'name', 'title', 'bio', 'photo', 'profile_pdf',
            'email', 'phone', 'location', 'social_links',
            'experience_years', 'projects_completed', 'clients_served',
            'meta_title', 'meta_description'
        )

    def update(self, instance, validated_data):
        # Handle file deletions
        if 'photo' in validated_data and validated_data['photo'] is None:
            instance.photo.delete(save=False)
        if 'profile_pdf' in validated_data and validated_data['profile_pdf'] is None:
            instance.profile_pdf.delete(save=False)
        
        return super().update(instance, validated_data)


class ServiceListSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    features = serializers.ListField(child=serializers.CharField(), required=False)

    class Meta:
        model = Service
        fields = (
            'id', 'title', 'slug', 'short_description', 'icon_name', 'icon_color',
            'image_url', 'features', 'display_price', 'cta_text', 'cta_link',
            'is_featured', 'order', 'created_at'
        )
        read_only_fields = ('id', 'slug', 'created_at')

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


class ServiceDetailSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    features = serializers.ListField(child=serializers.CharField(), required=False)

    class Meta:
        model = Service
        fields = (
            'id', 'title', 'slug', 'short_description', 'description',
            'icon_name', 'icon_color', 'image_url', 'features',
            'starting_price', 'price_unit', 'display_price',
            'cta_text', 'cta_link', 'is_featured', 'order',
            'meta_title', 'meta_description', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'slug', 'created_at', 'updated_at')

    def get_image_url(self, obj):
        if obj.image:
            return obj.image.url
        return None


class ServiceCreateSerializer(serializers.ModelSerializer):
    features = serializers.ListField(child=serializers.CharField(), required=False)

    class Meta:
        model = Service
        fields = (
            'title', 'slug', 'short_description', 'description',
            'icon_name', 'icon_color', 'image', 'features',
            'starting_price', 'price_unit', 'cta_text', 'cta_link',
            'is_published', 'is_featured', 'order',
            'meta_title', 'meta_description'
        )
        extra_kwargs = {
            'slug': {'required': False},
        }

    def create(self, validated_data):
        return Service.objects.create(**validated_data)

    def update(self, instance, validated_data):
        # Handle image deletion
        if 'image' in validated_data and validated_data['image'] is None:
            instance.image.delete(save=False)
        
        return super().update(instance, validated_data)