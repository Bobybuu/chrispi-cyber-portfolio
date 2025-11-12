#contact/serializers.py
from rest_framework import serializers
from django.core.validators import validate_email
from .models import ContactMessage, ContactSetting


class ContactMessageCreateSerializer(serializers.ModelSerializer):
    recaptcha_token = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = ContactMessage
        fields = (
            'name', 'email', 'phone', 'company', 'subject', 
            'message', 'category', 'consent_given', 
            'newsletter_subscribed', 'recaptcha_token'
        )
        extra_kwargs = {
            'consent_given': {'required': True},
        }

    def validate_email(self, value):
        validate_email(value)
        return value.lower()

    def validate_consent_given(self, value):
        if not value:
            raise serializers.ValidationError("Consent is required to process your message.")
        return value

    def create(self, validated_data):
        # Remove recaptcha_token from validated data as it's not a model field
        validated_data.pop('recaptcha_token', None)
        
        # Get IP address and user agent from request
        request = self.context.get('request')
        if request:
            validated_data['ip_address'] = self.get_client_ip(request)
            validated_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
            validated_data['referrer'] = request.META.get('HTTP_REFERER', '')
        
        return ContactMessage.objects.create(**validated_data)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ContactMessageListSerializer(serializers.ModelSerializer):
    short_message = serializers.ReadOnlyField()

    class Meta:
        model = ContactMessage
        fields = (
            'id', 'name', 'email', 'subject', 'short_message',
            'status', 'priority', 'source', 'category', 'is_processed',
            'response_sent', 'created_at'
        )
        read_only_fields = ('id', 'created_at')


class ContactMessageDetailSerializer(serializers.ModelSerializer):
    assigned_to_email = serializers.EmailField(source='assigned_to.email', read_only=True)

    class Meta:
        model = ContactMessage
        fields = (
            'id', 'name', 'email', 'phone', 'company', 'subject', 'message',
            'category', 'source', 'status', 'priority', 'is_processed',
            'assigned_to', 'assigned_to_email', 'internal_notes',
            'response_sent', 'response_notes', 'response_sent_at',
            'ip_address', 'user_agent', 'referrer',
            'consent_given', 'newsletter_subscribed', 'metadata',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')


class ContactMessageUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = (
            'status', 'priority', 'is_processed', 'assigned_to',
            'internal_notes', 'response_sent', 'response_notes'
        )

    def update(self, instance, validated_data):
        # Auto-set response timestamp if marking as replied
        if validated_data.get('response_sent') and not instance.response_sent:
            from django.utils import timezone
            instance.response_sent_at = timezone.now()
        
        return super().update(instance, validated_data)


class ContactSettingSerializer(serializers.ModelSerializer):
    notification_emails_list = serializers.ListField(
        child=serializers.EmailField(),
        read_only=True
    )
    available_categories = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )

    class Meta:
        model = ContactSetting
        fields = (
            'id', 'is_contact_form_enabled', 'require_name', 'require_email',
            'require_phone', 'require_company', 'require_subject',
            'rate_limit_enabled', 'rate_limit_period', 'rate_limit_count',
            'notify_on_new_message', 'notification_emails', 'notification_emails_list',
            'auto_response_enabled', 'auto_response_subject', 'auto_response_message',
            'recaptcha_enabled', 'recaptcha_site_key', 'available_categories',
            'updated_at'
        )
        read_only_fields = ('id', 'updated_at')


class ContactFormConfigSerializer(serializers.Serializer):
    """Serializer for public contact form configuration"""
    is_enabled = serializers.BooleanField()
    required_fields = serializers.DictField()
    categories = serializers.ListField(child=serializers.CharField())
    recaptcha_enabled = serializers.BooleanField()
    recaptcha_site_key = serializers.CharField(allow_blank=True)