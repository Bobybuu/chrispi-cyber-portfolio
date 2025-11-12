from django.contrib import admin
from django.utils.html import format_html
from .models import File, FileUploadRequest


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    list_display = (
        'original_filename', 
        'file_preview',
        'category_display',
        'uploaded_by_display',
        'file_size_display',
        'is_public',
        'is_approved',
        'download_count',
        'created_at_display'
    )
    list_filter = (
        'category', 'is_public', 'is_approved', 'virus_scan_status',
        'created_at', 'uploaded_by'
    )
    list_editable = ('is_public', 'is_approved')
    search_fields = ('original_filename', 'title', 'description', 'uploaded_by__email')
    readonly_fields = (
        'created_at', 'updated_at', 'file_size', 'mime_type', 
        'file_extension', 'download_count', 'last_downloaded_at',
        'file_preview_large', 'metadata_display'
    )
    date_hierarchy = 'created_at'
    actions = ['approve_files', 'mark_as_public', 'mark_as_private']
    
    fieldsets = (
        ('File Information', {
            'fields': ('file', 'file_preview_large', 'original_filename', 'title')
        }),
        ('Metadata', {
            'fields': ('description', 'alt_text', 'tags', 'category')
        }),
        ('Technical Information', {
            'fields': ('file_size', 'mime_type', 'file_extension', 'metadata_display')
        }),
        ('Permissions', {
            'fields': ('uploaded_by', 'is_public', 'is_approved', 'is_featured')
        }),
        ('Security', {
            'fields': ('virus_scan_status',)
        }),
        ('Usage', {
            'fields': ('download_count', 'last_downloaded_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def file_preview(self, obj):
        if obj.is_image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />', 
                obj.file_url
            )
        else:
            icon_color = {
                'document': 'blue',
                'pdf': 'red',
                'image': 'green',
                'video': 'purple',
                'audio': 'orange',
                'archive': 'brown',
                'other': 'gray',
            }.get(obj.category, 'gray')
            
            return format_html(
                '<div style="width: 50px; height: 50px; background: {}; color: white; '
                'display: flex; align-items: center; justify-content: center; '
                'font-weight: bold; border-radius: 4px;">.{}</div>',
                icon_color,
                obj.file_extension.upper()
            )
    file_preview.short_description = 'Preview'

    def file_preview_large(self, obj):
        if obj.is_image:
            return format_html(
                '<img src="{}" style="max-height: 300px; max-width: 100%;" />', 
                obj.file_url
            )
        return "No preview available"
    file_preview_large.short_description = 'Large Preview'

    def category_display(self, obj):
        category_colors = {
            'image': 'green',
            'document': 'blue',
            'pdf': 'red',
            'video': 'purple',
            'audio': 'orange',
            'archive': 'brown',
            'other': 'gray',
        }
        color = category_colors.get(obj.category, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_category_display()
        )
    category_display.short_description = 'Category'

    def uploaded_by_display(self, obj):
        return obj.uploaded_by.email
    uploaded_by_display.short_description = 'Uploaded By'
    uploaded_by_display.admin_order_field = 'uploaded_by__email'

    def file_size_display(self, obj):
        return obj.display_size
    file_size_display.short_description = 'Size'

    def created_at_display(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M')
    created_at_display.short_description = 'Created'

    def metadata_display(self, obj):
        if obj.metadata:
            return format_html(
                '<pre style="background: #f5f5f5; padding: 10px; border-radius: 4px; '
                'max-height: 200px; overflow: auto;">{}</pre>',
                str(obj.metadata)
            )
        return "No metadata"
    metadata_display.short_description = 'Metadata'

    def approve_files(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} files approved.')
    approve_files.short_description = "Approve selected files"

    def mark_as_public(self, request, queryset):
        updated = queryset.update(is_public=True)
        self.message_user(request, f'{updated} files marked as public.')
    mark_as_public.short_description = "Mark selected files as public"

    def mark_as_private(self, request, queryset):
        updated = queryset.update(is_public=False)
        self.message_user(request, f'{updated} files marked as private.')
    mark_as_private.short_description = "Mark selected files as private"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('uploaded_by')


@admin.register(FileUploadRequest)
class FileUploadRequestAdmin(admin.ModelAdmin):
    list_display = (
        'original_filename', 
        'uploaded_by_display',
        'file_size_display',
        'is_used',
        'is_expired_display',
        'created_at_display'
    )
    list_filter = ('is_used', 'created_at', 'uploaded_by')
    search_fields = ('original_filename', 'upload_token', 'uploaded_by__email')
    readonly_fields = (
        'created_at', 'expires_at', 'is_used', 'is_expired',
        'resulting_file_link'
    )
    date_hierarchy = 'created_at'

    def uploaded_by_display(self, obj):
        return obj.uploaded_by.email
    uploaded_by_display.short_description = 'Uploaded By'

    def file_size_display(self, obj):
        # Simple size display for admin
        if obj.file_size < 1024:
            return f"{obj.file_size} B"
        elif obj.file_size < 1024 * 1024:
            return f"{obj.file_size / 1024:.1f} KB"
        else:
            return f"{obj.file_size / (1024 * 1024):.1f} MB"
    file_size_display.short_description = 'Size'

    def is_expired_display(self, obj):
        if obj.is_expired:
            return format_html(
                '<span style="color: red; font-weight: bold;">EXPIRED</span>'
            )
        return format_html(
            '<span style="color: green; font-weight: bold;">ACTIVE</span>'
        )
    is_expired_display.short_description = 'Status'

    def created_at_display(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M')
    created_at_display.short_description = 'Created'

    def resulting_file_link(self, obj):
        if obj.resulting_file:
            return format_html(
                '<a href="{}">{}</a>',
                obj.resulting_file.file_url,
                obj.resulting_file.original_filename
            )
        return "No file uploaded"
    resulting_file_link.short_description = 'Resulting File'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('uploaded_by', 'resulting_file')