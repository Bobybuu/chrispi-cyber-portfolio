from rest_framework import serializers
from .models import AuditLog, SystemSetting, HealthCheck, APIRequestLog


class AuditLogListSerializer(serializers.ModelSerializer):
    performed_by_email = serializers.EmailField(source='performed_by.email', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    entity_display = serializers.CharField(source='get_entity_display', read_only=True)

    class Meta:
        model = AuditLog
        fields = (
            'id', 'action', 'action_display', 'entity', 'entity_display',
            'entity_id', 'performed_by_email', 'description', 'severity',
            'is_successful', 'created_at'
        )
        read_only_fields = ('id', 'created_at')


class AuditLogDetailSerializer(serializers.ModelSerializer):
    performed_by_email = serializers.EmailField(source='performed_by.email', read_only=True)

    class Meta:
        model = AuditLog
        fields = (
            'id', 'action', 'entity', 'entity_id', 'performed_by_email',
            'user_ip', 'user_agent', 'description', 'payload', 'changes',
            'severity', 'is_successful', 'error_message', 'created_at',
            'request_timestamp'
        )
        read_only_fields = ('id', 'created_at')


class SystemSettingSerializer(serializers.ModelSerializer):
    is_production = serializers.ReadOnlyField()

    class Meta:
        model = SystemSetting
        fields = (
            'id', 'site_name', 'site_description', 'contact_email',
            'maintenance_mode', 'maintenance_message',
            'max_login_attempts', 'login_timeout_minutes',
            'password_min_length', 'require_password_complexity',
            'api_rate_limit', 'cache_timeout', 'search_results_limit',
            'enable_registration', 'enable_comments', 'enable_newsletter', 'enable_analytics',
            'email_notifications', 'slack_notifications', 'slack_webhook_url',
            'auto_backup', 'backup_frequency_days', 'monitor_uptime',
            'theme_settings', 'custom_css', 'custom_js',
            'metadata', 'is_production', 'updated_at'
        )
        read_only_fields = ('id', 'updated_at')


class SystemSettingPublicSerializer(serializers.ModelSerializer):
    """Public serializer with limited fields"""
    class Meta:
        model = SystemSetting
        fields = (
            'site_name', 'site_description', 'contact_email',
            'maintenance_mode', 'maintenance_message'
        )
        read_only_fields = fields


class HealthCheckSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthCheck
        fields = (
            'id', 'check_type', 'is_successful', 'response_time',
            'error_message', 'server_hostname', 'python_version',
            'django_version', 'metadata', 'created_at'
        )
        read_only_fields = ('id', 'created_at')


class APIRequestLogSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = APIRequestLog
        fields = (
            'id', 'method', 'path', 'query_params', 'user_email',
            'is_authenticated', 'status_code', 'response_size',
            'response_time', 'error_message', 'exception_type',
            'ip_address', 'user_agent', 'metadata', 'created_at'
        )
        read_only_fields = ('id', 'created_at')


class SystemStatsSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    total_articles = serializers.IntegerField()
    total_portfolio_items = serializers.IntegerField()
    total_contact_messages = serializers.IntegerField()
    total_files = serializers.IntegerField()
    system_uptime = serializers.FloatField()
    database_size = serializers.FloatField()
    cache_hit_rate = serializers.FloatField()


class HealthCheckResponseSerializer(serializers.Serializer):
    status = serializers.CharField()
    timestamp = serializers.DateTimeField()
    response_time = serializers.FloatField()
    checks = serializers.DictField(child=serializers.BooleanField())
    details = serializers.DictField()