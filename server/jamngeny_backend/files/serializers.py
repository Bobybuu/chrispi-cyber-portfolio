from rest_framework import serializers
from .models import File, FileUploadRequest


class FileListSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    display_size = serializers.ReadOnlyField()
    uploaded_by_email = serializers.EmailField(source='uploaded_by.email', read_only=True)

    class Meta:
        model = File
        fields = (
            'id', 'original_filename', 'file_url', 'title', 'description',
            'category', 'file_extension', 'display_size', 'mime_type',
            'is_public', 'is_approved', 'is_featured', 'download_count',
            'uploaded_by_email', 'created_at'
        )
        read_only_fields = ('id', 'created_at')


class FileDetailSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    display_size = serializers.ReadOnlyField()
    uploaded_by_email = serializers.EmailField(source='uploaded_by.email', read_only=True)
    tags = serializers.ListField(child=serializers.CharField(), required=False)

    class Meta:
        model = File
        fields = (
            'id', 'original_filename', 'file_url', 'title', 'description', 'alt_text',
            'category', 'file_extension', 'display_size', 'mime_type', 'file_size',
            'tags', 'metadata', 'is_public', 'is_approved', 'is_featured',
            'virus_scan_status', 'download_count', 'last_downloaded_at',
            'uploaded_by_email', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class FileCreateSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(child=serializers.CharField(), required=False)

    class Meta:
        model = File
        fields = (
            'file', 'title', 'description', 'alt_text', 'category',
            'tags', 'is_public', 'is_featured'
        )
        extra_kwargs = {
            'file': {'required': True},
        }

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['uploaded_by'] = request.user
        return super().create(validated_data)


class FileUpdateSerializer(serializers.ModelSerializer):
    tags = serializers.ListField(child=serializers.CharField(), required=False)

    class Meta:
        model = File
        fields = (
            'title', 'description', 'alt_text', 'category',
            'tags', 'is_public', 'is_featured', 'is_approved'
        )


class FileUploadRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileUploadRequest
        fields = (
            'id', 'original_filename', 'file_size', 'mime_type',
            'file_extension', 'purpose', 'expires_at', 'upload_token'
        )
        read_only_fields = ('id', 'upload_token', 'expires_at')


class PresignedUploadResponseSerializer(serializers.Serializer):
    upload_url = serializers.URLField()
    upload_token = serializers.CharField()
    expires_at = serializers.DateTimeField()
    fields = serializers.DictField(child=serializers.CharField())


class FileUploadCompleteSerializer(serializers.Serializer):
    upload_token = serializers.CharField()
    file_data = serializers.DictField()

    def validate_upload_token(self, value):
        try:
            upload_request = FileUploadRequest.objects.get(upload_token=value)
            if not upload_request.is_valid:
                raise serializers.ValidationError("Upload token is invalid or expired.")
            return value
        except FileUploadRequest.DoesNotExist:
            raise serializers.ValidationError("Invalid upload token.")