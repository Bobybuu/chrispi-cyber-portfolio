import uuid
import json
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex

User = get_user_model()


class AuditLog(models.Model):
    """
    Comprehensive audit logging for all system activities
    """
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('download', 'Download'),
        ('upload', 'Upload'),
        ('export', 'Export'),
        ('import', 'Import'),
        ('approve', 'Approve'),
        ('reject', 'Reject'),
        ('publish', 'Publish'),
        ('unpublish', 'Unpublish'),
        ('other', 'Other'),
    ]

    ENTITY_CHOICES = [
        ('user', 'User'),
        ('article', 'Article'),
        ('portfolio', 'Portfolio Item'),
        ('service', 'Service'),
        ('file', 'File'),
        ('contact_message', 'Contact Message'),
        ('tag', 'Tag'),
        ('category', 'Category'),
        ('system', 'System'),
        ('auth', 'Authentication'),
        ('api', 'API'),
    ]

    SEVERITY_CHOICES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Action Information
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    entity = models.CharField(max_length=50, choices=ENTITY_CHOICES)
    entity_id = models.CharField(max_length=100, blank=True, help_text="ID of the affected entity")
    
    # User & Session
    performed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='audit_logs'
    )
    user_ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    session_key = models.CharField(max_length=100, blank=True)
    
    # Content
    description = models.TextField(help_text="Human-readable description of the action")
    payload = models.JSONField(
        default=dict,
        blank=True,
        help_text="Detailed action data (changes, parameters, etc.)"
    )
    changes = models.JSONField(
        default=dict,
        blank=True,
        help_text="Field-level changes (for update actions)"
    )
    
    # Metadata
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='info')
    is_successful = models.BooleanField(default=True)
    error_message = models.TextField(blank=True, help_text="Error message if action failed")
    
    # Search
    search_vector = SearchVectorField(null=True, editable=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    request_timestamp = models.DateTimeField(
        default=timezone.now,
        help_text="Timestamp when the action was requested"
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            GinIndex(fields=['search_vector']),
            models.Index(fields=['entity', 'entity_id']),
            models.Index(fields=['action', 'created_at']),
            models.Index(fields=['performed_by', 'created_at']),
            models.Index(fields=['severity', 'created_at']),
        ]
        verbose_name = 'Audit Log'
        verbose_name_plural = 'Audit Logs'

    def __str__(self):
        return f"{self.get_action_display()} {self.get_entity_display()} by {self.get_user_display()}"

    def get_user_display(self):
        """Get user display name"""
        if self.performed_by:
            return self.performed_by.email
        return "System" if not self.user_ip else f"Anonymous ({self.user_ip})"

    def save(self, *args, **kwargs):
        # Auto-set description if not provided
        if not self.description:
            self.description = self.generate_description()
        
        super().save(*args, **kwargs)

    def generate_description(self):
        """Generate automatic description based on action and entity"""
        entity_name = self.get_entity_display().lower()
        
        if self.action == 'create':
            return f"Created {entity_name} {self.entity_id or ''}"
        elif self.action == 'update':
            return f"Updated {entity_name} {self.entity_id or ''}"
        elif self.action == 'delete':
            return f"Deleted {entity_name} {self.entity_id or ''}"
        elif self.action == 'login':
            return f"User logged in"
        elif self.action == 'logout':
            return f"User logged out"
        else:
            return f"{self.get_action_display()} {entity_name} {self.entity_id or ''}"

    @property
    def is_high_severity(self):
        """Check if log is high severity"""
        return self.severity in ['error', 'critical']

    @property
    def changes_summary(self):
        """Get summary of changes for display"""
        if self.changes:
            changes_list = []
            for field, (old_value, new_value) in self.changes.items():
                changes_list.append(f"{field}: {old_value} → {new_value}")
            return "; ".join(changes_list)
        return "No changes"

    @classmethod
    def log_action(cls, action, entity, performed_by=None, entity_id=None, 
                   description=None, payload=None, changes=None, severity='info',
                   user_ip=None, user_agent=None, session_key=None, is_successful=True,
                   error_message=''):
        """Convenience method to create audit logs"""
        return cls.objects.create(
            action=action,
            entity=entity,
            entity_id=str(entity_id) if entity_id else '',
            performed_by=performed_by,
            description=description,
            payload=payload or {},
            changes=changes or {},
            severity=severity,
            is_successful=is_successful,
            error_message=error_message,
            user_ip=user_ip,
            user_agent=user_agent or '',
            session_key=session_key or ''
        )


class SystemSetting(models.Model):
    """
    Singleton model for system-wide settings
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Site Information
    site_name = models.CharField(max_length=200, default='Jamngeny Vision')
    site_description = models.TextField(blank=True, default='ICT, Cybersecurity, and Strategic Writing Portfolio')
    contact_email = models.EmailField(default='jamngeny@gmail.com')
    
    # Maintenance
    maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.TextField(blank=True, default='Site is under maintenance. Please check back later.')
    
    # Security
    max_login_attempts = models.PositiveIntegerField(default=5)
    login_timeout_minutes = models.PositiveIntegerField(default=30)
    password_min_length = models.PositiveIntegerField(default=8)
    require_password_complexity = models.BooleanField(default=True)
    
    # API & Performance
    api_rate_limit = models.PositiveIntegerField(default=1000, help_text="Requests per hour per user")
    cache_timeout = models.PositiveIntegerField(default=300, help_text="Cache timeout in seconds")
    search_results_limit = models.PositiveIntegerField(default=50)
    
    # Features
    enable_registration = models.BooleanField(default=False)
    enable_comments = models.BooleanField(default=False)
    enable_newsletter = models.BooleanField(default=False)
    enable_analytics = models.BooleanField(default=True)
    
    # Notifications
    email_notifications = models.BooleanField(default=True)
    slack_notifications = models.BooleanField(default=False)
    slack_webhook_url = models.URLField(blank=True)
    
    # Backup & Monitoring
    auto_backup = models.BooleanField(default=False)
    backup_frequency_days = models.PositiveIntegerField(default=7)
    monitor_uptime = models.BooleanField(default=True)
    
    # Customization
    theme_settings = models.JSONField(
        default=dict,
        blank=True,
        help_text="Theme customization settings"
    )
    custom_css = models.TextField(blank=True, help_text="Custom CSS code")
    custom_js = models.TextField(blank=True, help_text="Custom JavaScript code")
    
    # Metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional system metadata"
    )
    
    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'System Setting'
        verbose_name_plural = 'System Settings'

    def __str__(self):
        return "System Settings"

    def save(self, *args, **kwargs):
        # Enforce singleton pattern by checking if any instance exists
        if not self.pk and SystemSetting.objects.exists():
            # Update the existing instance instead of creating a new one
            existing = SystemSetting.objects.first()
            for field in self._meta.fields:
                if field.name != 'id':  # Don't copy the ID
                    setattr(existing, field.name, getattr(self, field.name))
            existing.save()
            return
        super().save(*args, **kwargs)

    @classmethod
    def get_instance(cls):
        """Get or create the singleton instance"""
        if cls.objects.exists():
            return cls.objects.first()
        else:
            return cls.objects.create(
                site_name='Jamngeny Vision',
                site_description='ICT, Cybersecurity, and Strategic Writing Portfolio',
                contact_email='jamngeny@gmail.com'
            )

    @property
    def is_production(self):
        """Check if system is in production mode"""
        from django.conf import settings
        return not settings.DEBUG


class HealthCheck(models.Model):
    """
    Track system health check results
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Check Information
    check_type = models.CharField(
        max_length=50,
        choices=[
            ('database', 'Database'),
            ('cache', 'Cache'),
            ('storage', 'Storage'),
            ('external_api', 'External API'),
            ('celery', 'Celery'),
            ('full', 'Full System'),
        ]
    )
    
    # Results
    is_successful = models.BooleanField()
    response_time = models.FloatField(help_text="Response time in milliseconds")
    error_message = models.TextField(blank=True)
    
    # System Info
    server_hostname = models.CharField(max_length=200, blank=True)
    python_version = models.CharField(max_length=50, blank=True)
    django_version = models.CharField(max_length=50, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['check_type', 'created_at']),
            models.Index(fields=['is_successful', 'created_at']),
        ]

    def __str__(self):
        status = "PASS" if self.is_successful else "FAIL"
        return f"{self.check_type} - {status} - {self.created_at}"

    @classmethod
    def log_check(cls, check_type, is_successful, response_time, error_message='', 
                  metadata=None):
        """Convenience method to log health checks"""
        import socket
        import sys
        
        return cls.objects.create(
            check_type=check_type,
            is_successful=is_successful,
            response_time=response_time,
            error_message=error_message,
            server_hostname=socket.gethostname(),
            python_version=sys.version.split()[0],
            django_version=cls.get_django_version(),
            metadata=metadata or {}
        )

    @staticmethod
    def get_django_version():
        """Get Django version"""
        import django
        return django.get_version()


class APIRequestLog(models.Model):
    """
    Log all API requests for analytics and debugging
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Request Information
    method = models.CharField(max_length=10)
    path = models.CharField(max_length=500)
    query_params = models.JSONField(default=dict, blank=True)
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField()
    
    # User & Authentication
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='api_requests'
    )
    is_authenticated = models.BooleanField(default=False)
    
    # Response
    status_code = models.PositiveIntegerField()
    response_size = models.PositiveIntegerField(default=0, help_text="Response size in bytes")
    response_time = models.FloatField(help_text="Response time in milliseconds")
    
    # Errors
    error_message = models.TextField(blank=True)
    exception_type = models.CharField(max_length=200, blank=True)
    
    # Metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    requested_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['path', 'created_at']),
            models.Index(fields=['method', 'created_at']),
            models.Index(fields=['status_code', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]
        verbose_name = 'API Request Log'
        verbose_name_plural = 'API Request Logs'

    def __str__(self):
        return f"{self.method} {self.path} - {self.status_code}"

    @property
    def is_error(self):
        """Check if response was an error"""
        return self.status_code >= 400

    @property
    def is_slow(self):
        """Check if response was slow (> 1 second)"""
        return self.response_time > 1000

    @classmethod
    def log_request(cls, request, response, response_time, user=None, 
                    exception=None, metadata=None):
        """Convenience method to log API requests"""
        from django.utils import timezone
        
        # Extract request data
        method = request.method
        path = request.path
        query_params = dict(request.GET)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        ip_address = cls.get_client_ip(request)
        
        # Extract response data
        status_code = response.status_code
        response_size = len(response.content) if hasattr(response, 'content') else 0
        
        # Handle errors
        error_message = ''
        exception_type = ''
        if exception:
            error_message = str(exception)
            exception_type = type(exception).__name__
        
        return cls.objects.create(
            method=method,
            path=path,
            query_params=query_params,
            user_agent=user_agent,
            ip_address=ip_address,
            user=user,
            is_authenticated=user.is_authenticated if user else False,
            status_code=status_code,
            response_size=response_size,
            response_time=response_time,
            error_message=error_message,
            exception_type=exception_type,
            metadata=metadata or {},
            requested_at=timezone.now()
        )

    @staticmethod
    def get_client_ip(request):
        """Extract client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip