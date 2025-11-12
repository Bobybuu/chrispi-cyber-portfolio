from django.contrib import admin
from django.utils.html import format_html
from .models import About, Service


@admin.register(About)
class AboutAdmin(admin.ModelAdmin):
    list_display = ('name', 'title', 'experience_years', 'updated_at')
    readonly_fields = (
        'created_at', 'updated_at', 'sanitized_bio', 
        'photo_preview', 'pdf_preview', 'social_links_display'
    )
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'title', 'bio', 'sanitized_bio')
        }),
        ('Media', {
            'fields': ('photo', 'photo_preview', 'profile_pdf', 'pdf_preview')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'location', 'social_links', 'social_links_display')
        }),
        ('Statistics', {
            'fields': ('experience_years', 'projects_completed', 'clients_served')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def has_add_permission(self, request):
        # Allow only one About instance
        if About.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the About instance
        return False

    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 100%;" />', 
                obj.photo.url
            )
        return "No photo uploaded"
    photo_preview.short_description = 'Photo Preview'

    def pdf_preview(self, obj):
        if obj.profile_pdf:
            return format_html(
                '<a href="{}" target="_blank">View PDF</a>', 
                obj.profile_pdf.url
            )
        return "No PDF uploaded"
    pdf_preview.short_description = 'PDF Preview'

    def social_links_display(self, obj):
        if obj.social_links:
            links_html = []
            for platform, url in obj.social_links.items():
                if url:
                    links_html.append(
                        f'<div><strong>{platform.title()}:</strong> <a href="{url}" target="_blank">{url}</a></div>'
                    )
            return format_html(''.join(links_html))
        return "No social links configured"
    social_links_display.short_description = 'Social Links Preview'


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = (
        'title', 
        'slug', 
        'order', 
        'is_published', 
        'is_featured',
        'display_price_display',
        'created_at'
    )
    list_filter = ('is_published', 'is_featured', 'created_at')
    list_editable = ('order', 'is_published', 'is_featured')
    search_fields = ('title', 'description', 'short_description', 'features')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at', 'image_preview')
    ordering = ('order', 'title')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'short_description', 'description')
        }),
        ('Display', {
            'fields': ('icon_name', 'icon_color', 'order', 'image', 'image_preview')
        }),
        ('Features', {
            'fields': ('features',)
        }),
        ('Pricing & CTA', {
            'fields': ('starting_price', 'price_unit', 'cta_text', 'cta_link')
        }),
        ('Publication', {
            'fields': ('is_published', 'is_featured')
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def display_price_display(self, obj):
        return obj.display_price or "—"
    display_price_display.short_description = 'Price'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 200px; max-width: 100%;" />', 
                obj.image.url
            )
        return "No image uploaded"
    image_preview.short_description = 'Image Preview'
