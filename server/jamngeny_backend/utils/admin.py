from django.contrib import admin
from django.utils.html import format_html
from .models import AuditLog, SystemSetting, HealthCheck, APIRequestLog
from django.utils import timezone
import json
@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        'action_display',
        'entity_display', 
        'entity_id_short',
        'user_display',
        'severity_display',
        'is_successful_display',
        'created_at_display'
    )
    list_filter = (
        'action', 'entity', 'severity', 'is_successful', 
        'created_at', 'performed_by'
    )
    search_fields = (
        'description', 'entity_id', 'performed_by__email',
        'user_ip', 'error_message'
    )
    readonly_fields = (
        'created_at', 'request_timestamp', 'user_display',
        'changes_summary_display', 'payload_display'
    )
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Action Information', {
            'fields': ('action', 'entity', 'entity_id', 'description')
        }),
        ('User Information', {
            'fields': ('user_display', 'user_ip', 'user_agent', 'session_key')
        }),
        ('Results', {
            'fields': ('severity', 'is_successful', 'error_message')
        }),
        ('Data', {
            'fields': ('changes_summary_display', 'payload_display')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'request_timestamp')
        }),
    )

    def action_display(self, obj):
        action_colors = {
            'create': 'green',
            'update': 'blue',
            'delete': 'red',
            'login': 'orange',
            'logout': 'gray',
            'view': 'purple',
        }
        color = action_colors.get(obj.action, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_action_display()
        )
    action_display.short_description = 'Action'

    def entity_display(self, obj):
        return obj.get_entity_display()
    entity_display.short_description = 'Entity'

    def entity_id_short(self, obj):
        return obj.entity_id[:20] + '...' if len(obj.entity_id) > 20 else obj.entity_id
    entity_id_short.short_description = 'Entity ID'

    def user_display(self, obj):
        return obj.get_user_display()
    user_display.short_description = 'User'

    def severity_display(self, obj):
        severity_colors = {
            'info': 'blue',
            'warning': 'orange',
            'error': 'red',
            'critical': 'darkred',
        }
        color = severity_colors.get(obj.severity, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_severity_display().upper()
        )
    severity_display.short_description = 'Severity'

    def is_successful_display(self, obj):
        if obj.is_successful:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ SUCCESS</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ FAILED</span>'
            )
    is_successful_display.short_description = 'Status'

    def created_at_display(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M')
    created_at_display.short_description = 'Created'

    def changes_summary_display(self, obj):
        return obj.changes_summary or 'No changes'
    changes_summary_display.short_description = 'Changes Summary'

    def payload_display(self, obj):
        if obj.payload:
            return format_html(
                '<pre style="background: #f5f5f5; padding: 10px; border-radius: 4px; '
                'max-height: 300px; overflow: auto;">{}</pre>',
                json.dumps(obj.payload, indent=2, default=str)
            )
        return "No payload data"
    payload_display.short_description = 'Payload Data'

    def has_add_permission(self, request):
        # Audit logs should only be created automatically
        return False

    def has_change_permission(self, request, obj=None):
        # Audit logs should not be modified
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('performed_by')


@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'maintenance_mode', 'updated_at_display')
    readonly_fields = ('updated_at', 'created_at', 'is_production_display')
    
    fieldsets = (
        ('Site Information', {
            'fields': ('site_name', 'site_description', 'contact_email')
        }),
        ('Maintenance', {
            'fields': ('maintenance_mode', 'maintenance_message')
        }),
        ('Security', {
            'fields': (
                'max_login_attempts', 'login_timeout_minutes',
                'password_min_length', 'require_password_complexity'
            )
        }),
        ('API & Performance', {
            'fields': ('api_rate_limit', 'cache_timeout', 'search_results_limit')
        }),
        ('Features', {
            'fields': (
                'enable_registration', 'enable_comments', 
                'enable_newsletter', 'enable_analytics'
            )
        }),
        ('Notifications', {
            'fields': ('email_notifications', 'slack_notifications', 'slack_webhook_url')
        }),
        ('Backup & Monitoring', {
            'fields': ('auto_backup', 'backup_frequency_days', 'monitor_uptime')
        }),
        ('Customization', {
            'fields': ('theme_settings', 'custom_css', 'custom_js')
        }),
        ('Metadata', {
            'fields': ('metadata',)
        }),
        ('System Info', {
            'fields': ('is_production_display', 'created_at', 'updated_at')
        }),
    )

    def has_add_permission(self, request):
        # Allow only one SystemSetting instance
        if SystemSetting.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the SystemSetting instance
        return False

    def updated_at_display(self, obj):
        return obj.updated_at.strftime('%Y-%m-%d %H:%M')
    updated_at_display.short_description = 'Last Updated'

    def is_production_display(self, obj):
        if obj.is_production:
            return format_html(
                '<span style="color: green; font-weight: bold;">PRODUCTION</span>'
            )
        else:
            return format_html(
                '<span style="color: orange; font-weight: bold;">DEVELOPMENT</span>'
            )
    is_production_display.short_description = 'Environment'


@admin.register(HealthCheck)
class HealthCheckAdmin(admin.ModelAdmin):
    list_display = (
        'check_type_display',
        'status_display',
        'response_time_display',
        'server_hostname',
        'created_at_display'
    )
    list_filter = ('check_type', 'is_successful', 'created_at')
    search_fields = ('error_message', 'server_hostname')
    readonly_fields = ('created_at', 'metadata_display')
    date_hierarchy = 'created_at'

    def check_type_display(self, obj):
        return obj.get_check_type_display()
    check_type_display.short_description = 'Check Type'

    def status_display(self, obj):
        if obj.is_successful:
            return format_html(
                '<span style="color: green; font-weight: bold;">HEALTHY</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">UNHEALTHY</span>'
            )
    status_display.short_description = 'Status'

    def response_time_display(self, obj):
        color = 'green' if obj.response_time < 1000 else 'orange' if obj.response_time < 5000 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.0f} ms</span>',
            color,
            obj.response_time
        )
    response_time_display.short_description = 'Response Time'

    def created_at_display(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M')
    created_at_display.short_description = 'Checked'

    def metadata_display(self, obj):
        if obj.metadata:
            return format_html(
                '<pre style="background: #f5f5f5; padding: 10px; border-radius: 4px; '
                'max-height: 200px; overflow: auto;">{}</pre>',
                json.dumps(obj.metadata, indent=2, default=str)
            )
        return "No metadata"
    metadata_display.short_description = 'Metadata'

    def has_add_permission(self, request):
        # Health checks should only be created automatically
        return False

    def has_change_permission(self, request, obj=None):
        # Health checks should not be modified
        return False


@admin.register(APIRequestLog)
class APIRequestLogAdmin(admin.ModelAdmin):
    list_display = (
        'method_path_display',
        'status_code_display',
        'user_display',
        'response_time_display',
        'created_at_display'
    )
    list_filter = ('method', 'status_code', 'is_authenticated', 'created_at')
    search_fields = ('path', 'user__email', 'ip_address', 'error_message')
    readonly_fields = ('created_at', 'requested_at', 'query_params_display', 'metadata_display')
    date_hierarchy = 'created_at'

    def method_path_display(self, obj):
        method_colors = {
            'GET': 'green',
            'POST': 'blue',
            'PUT': 'orange',
            'PATCH': 'purple',
            'DELETE': 'red',
        }
        color = method_colors.get(obj.method, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span> {}',
            color,
            obj.method,
            obj.path[:50] + '...' if len(obj.path) > 50 else obj.path
        )
    method_path_display.short_description = 'Request'

    def status_code_display(self, obj):
        if obj.status_code < 400:
            color = 'green'
        elif obj.status_code < 500:
            color = 'orange'
        else:
            color = 'red'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.status_code
        )
    status_code_display.short_description = 'Status'

    def user_display(self, obj):
        if obj.user:
            return obj.user.email
        return f"Anonymous ({obj.ip_address})"
    user_display.short_description = 'User'

    def response_time_display(self, obj):
        color = 'green' if obj.response_time < 1000 else 'orange' if obj.response_time < 5000 else 'red'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.0f} ms</span>',
            color,
            obj.response_time
        )
    response_time_display.short_description = 'Response Time'

    def created_at_display(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M')
    created_at_display.short_description = 'Time'

    def query_params_display(self, obj):
        if obj.query_params:
            return format_html(
                '<pre style="background: #f5f5f5; padding: 10px; border-radius: 4px; '
                'max-height: 200px; overflow: auto;">{}</pre>',
                json.dumps(obj.query_params, indent=2, default=str)
            )
        return "No query parameters"
    query_params_display.short_description = 'Query Parameters'

    def metadata_display(self, obj):
        if obj.metadata:
            return format_html(
                '<pre style="background: #f5f5f5; padding: 10px; border-radius: 4px; '
                'max-height: 200px; overflow: auto;">{}</pre>',
                json.dumps(obj.metadata, indent=2, default=str)
            )
        return "No metadata"
    metadata_display.short_description = 'Metadata'

    def has_add_permission(self, request):
        # API request logs should only be created automatically
        return False

    def has_change_permission(self, request, obj=None):
        # API request logs should not be modified
        return False

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')