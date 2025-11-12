#contact/models.py
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class ContactMessage(models.Model):
    SOURCE_CHOICES = [
        ('website', 'Website Form'),
        ('api', 'API'),
        ('admin', 'Admin Panel'),
        ('email', 'Email'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('new', 'New'),
        ('read', 'Read'),
        ('replied', 'Replied'),
        ('archived', 'Archived'),
        ('spam', 'Spam'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Contact Information
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=200, blank=True, help_text="Company/organization name")
    
    # Message Content
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    
    # Categorization
    category = models.CharField(
        max_length=50, 
        blank=True,
        help_text="Message category (e.g., 'consulting', 'writing', 'general')"
    )
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='website')
    
    # Processing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    is_processed = models.BooleanField(default=False)
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='assigned_contacts',
        help_text="Team member assigned to handle this message"
    )
    
    # Response Tracking
    internal_notes = models.TextField(blank=True, help_text="Internal notes for team members")
    response_sent = models.BooleanField(default=False)
    response_notes = models.TextField(blank=True, help_text="Notes about the response sent")
    response_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Technical Information
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True, help_text="HTTP referrer if available")
    
    # Consent & Compliance
    consent_given = models.BooleanField(
        default=True,
        help_text="User consent for data processing"
    )
    newsletter_subscribed = models.BooleanField(
        default=False,
        help_text="User subscribed to newsletter"
    )
    
    # Metadata
    metadata = models.JSONField(
        default=dict, 
        blank=True,
        help_text="Additional metadata (form fields, etc.)"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['email', 'created_at']),
            models.Index(fields=['source', 'created_at']),
            models.Index(fields=['is_processed', 'created_at']),
        ]
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'

    def __str__(self):
        return f"{self.name} - {self.subject or 'No Subject'}"

    def save(self, *args, **kwargs):
        # Auto-set status based on is_processed
        if self.is_processed and self.status == 'new':
            self.status = 'read'
        
        # Auto-set response timestamp
        if self.response_sent and not self.response_sent_at:
            self.response_sent_at = timezone.now()
        
        super().save(*args, **kwargs)

    @property
    def is_recent(self):
        """Check if message is from the last 24 hours"""
        return self.created_at >= timezone.now() - timezone.timedelta(hours=24)

    @property
    def display_subject(self):
        """Get display subject with fallback"""
        return self.subject or "No Subject"

    @property
    def short_message(self):
        """Get truncated message for listings"""
        return self.message[:100] + "..." if len(self.message) > 100 else self.message

    def mark_as_read(self):
        """Mark message as read"""
        self.status = 'read'
        self.is_processed = True
        self.save()

    def mark_as_replied(self):
        """Mark message as replied"""
        self.status = 'replied'
        self.response_sent = True
        self.response_sent_at = timezone.now()
        self.save()


class ContactSetting(models.Model):
    """
    Singleton model for contact form settings
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Form Settings
    is_contact_form_enabled = models.BooleanField(default=True)
    require_name = models.BooleanField(default=True)
    require_email = models.BooleanField(default=True)
    require_phone = models.BooleanField(default=False)
    require_company = models.BooleanField(default=False)
    require_subject = models.BooleanField(default=False)
    
    # Rate Limiting
    rate_limit_enabled = models.BooleanField(default=True)
    rate_limit_period = models.PositiveIntegerField(
        default=3600,  # 1 hour in seconds
        help_text="Rate limit period in seconds"
    )
    rate_limit_count = models.PositiveIntegerField(
        default=5,
        help_text="Maximum number of messages per period"
    )
    
    # Notifications
    notify_on_new_message = models.BooleanField(default=True)
    notification_emails = models.TextField(
        blank=True,
        help_text="Comma-separated list of email addresses to notify"
    )
    
    # Auto-Response
    auto_response_enabled = models.BooleanField(default=True)
    auto_response_subject = models.CharField(max_length=200, blank=True)
    auto_response_message = models.TextField(blank=True)
    
    # Spam Protection
    recaptcha_enabled = models.BooleanField(default=False)
    recaptcha_site_key = models.CharField(max_length=100, blank=True)
    recaptcha_secret_key = models.CharField(max_length=100, blank=True)
    
    # Categories
    available_categories = models.JSONField(
        default=list,
        blank=True,
        help_text="Available contact categories as JSON array"
    )
    
    # Timestamps
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Contact Settings'
        verbose_name_plural = 'Contact Settings'

    def __str__(self):
        return "Contact Form Settings"

    def save(self, *args, **kwargs):
        # Enforce singleton pattern by checking if any instance exists
        if not self.pk and ContactSetting.objects.exists():
            # Update the existing instance instead of creating a new one
            existing = ContactSetting.objects.first()
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
                auto_response_subject='Thank you for your message',
                auto_response_message='Thank you for contacting us. We have received your message and will get back to you soon.',
                available_categories=['general', 'consulting', 'writing', 'support', 'other']
            )

    @property
    def notification_emails_list(self):
        """Get notification emails as list"""
        if self.notification_emails:
            return [email.strip() for email in self.notification_emails.split(',')]
        return []