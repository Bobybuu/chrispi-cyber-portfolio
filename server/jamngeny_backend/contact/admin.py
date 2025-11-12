#contact/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import ContactMessage, ContactSetting


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = (
        'name', 
        'email', 
        'subject_display', 
        'source', 
        'status',  # Use actual field name
        'priority',  # Use actual field name
        'is_processed',
        'created_at_display'
    )
    list_filter = (
        'status', 'priority', 'source', 'category', 
        'is_processed', 'response_sent', 'created_at'
    )
    list_editable = ('status', 'priority', 'is_processed')
    search_fields = ('name', 'email', 'subject', 'message', 'company')
    readonly_fields = (
        'created_at', 'updated_at', 'ip_address', 'user_agent', 
        'referrer', 'response_sent_at', 'short_message_display'
    )
    date_hierarchy = 'created_at'
    actions = ['mark_as_read', 'mark_as_replied', 'mark_as_spam']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone', 'company')
        }),
        ('Message Content', {
            'fields': ('subject', 'short_message_display', 'message', 'category')
        }),
        ('Processing', {
            'fields': ('status', 'priority', 'is_processed', 'assigned_to')
        }),
        ('Response', {
            'fields': ('response_sent', 'response_notes', 'response_sent_at')
        }),
        ('Internal Notes', {
            'fields': ('internal_notes',)
        }),
        ('Technical Information', {
            'fields': ('source', 'ip_address', 'user_agent', 'referrer')
        }),
        ('Consent', {
            'fields': ('consent_given', 'newsletter_subscribed')
        }),
        ('Metadata', {
            'fields': ('metadata',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def subject_display(self, obj):
        return obj.display_subject
    subject_display.short_description = 'Subject'

    def created_at_display(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M')
    created_at_display.short_description = 'Created'

    def short_message_display(self, obj):
        return obj.short_message
    short_message_display.short_description = 'Message Preview'

    def has_add_permission(self, request):
        # Contact messages should only be created via API
        return False

    def mark_as_read(self, request, queryset):
        updated = queryset.update(status='read', is_processed=True)
        self.message_user(request, f'{updated} messages marked as read.')
    mark_as_read.short_description = "Mark selected messages as read"

    def mark_as_replied(self, request, queryset):
        updated = queryset.update(
            status='replied', 
            response_sent=True, 
            response_sent_at=timezone.now()
        )
        self.message_user(request, f'{updated} messages marked as replied.')
    mark_as_replied.short_description = "Mark selected messages as replied"

    def mark_as_spam(self, request, queryset):
        updated = queryset.update(status='spam', is_processed=True)
        self.message_user(request, f'{updated} messages marked as spam.')
    mark_as_spam.short_description = "Mark selected messages as spam"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('assigned_to')


@admin.register(ContactSetting)
class ContactSettingAdmin(admin.ModelAdmin):
    list_display = ('is_contact_form_enabled', 'rate_limit_enabled', 'notify_on_new_message', 'updated_at')
    readonly_fields = ('updated_at',)

    def has_add_permission(self, request):
        # Allow only one ContactSetting instance
        if ContactSetting.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the ContactSetting instance
        return False