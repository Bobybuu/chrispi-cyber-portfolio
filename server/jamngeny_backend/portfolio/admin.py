#portfolio/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import PortfolioCategory, PortfolioItem, PortfolioImage


class PortfolioImageInline(admin.TabularInline):
    model = PortfolioImage
    extra = 1
    fields = ('image', 'caption', 'alt_text', 'order', 'is_featured')
    ordering = ('order',)


class SecondaryCategoriesInline(admin.TabularInline):
    model = PortfolioItem.secondary_categories.through
    extra = 1
    verbose_name = "Secondary Category"
    verbose_name_plural = "Secondary Categories"


@admin.register(PortfolioCategory)
class PortfolioCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'published_items_count', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    list_editable = ('order', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at', 'published_items_count')
    ordering = ('order', 'name')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description')
        }),
        ('Display', {
            'fields': ('order', 'is_active')
        }),
        ('Statistics', {
            'fields': ('published_items_count',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = (
        'title', 
        'category_display', 
        'client_display',
        'project_date_display', 
        'is_published', 
        'is_featured',
        'created_at'
    )
    list_filter = ('is_published', 'is_featured', 'category', 'project_date', 'created_at')
    list_editable = ('is_published', 'is_featured')
    search_fields = ('title', 'summary', 'content', 'client', 'technologies')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at', 'sanitized_content')
    date_hierarchy = 'project_date'
    inlines = [PortfolioImageInline, SecondaryCategoriesInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'category', 'summary', 'meta_description')
        }),
        ('Content', {
            'fields': ('content', 'sanitized_content')
        }),
        ('Project Details', {
            'fields': ('client', 'project_date', 'duration', 'link', 'technologies')
        }),
        ('Media', {
            'fields': ('featured_image',)
        }),
        ('Publication', {
            'fields': ('is_published', 'is_featured')
        }),
        ('Additional Data', {
            'fields': ('metadata',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def category_display(self, obj):
        return obj.category.name
    category_display.short_description = 'Category'
    category_display.admin_order_field = 'category__name'
    
    def client_display(self, obj):
        return obj.client if obj.client else "—"
    client_display.short_description = 'Client'
    
    def project_date_display(self, obj):
        return obj.project_date.strftime('%b %Y')
    project_date_display.short_description = 'Project Date'
    project_date_display.admin_order_field = 'project_date'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category').prefetch_related('secondary_categories', 'images')


@admin.register(PortfolioImage)
class PortfolioImageAdmin(admin.ModelAdmin):
    list_display = ('portfolio_item_display', 'image_preview', 'caption', 'order', 'is_featured', 'created_at')
    list_filter = ('is_featured', 'created_at', 'portfolio_item__category')
    list_editable = ('order', 'is_featured')
    search_fields = ('portfolio_item__title', 'caption', 'alt_text')
    readonly_fields = ('created_at', 'image_preview_large')
    
    def portfolio_item_display(self, obj):
        return obj.portfolio_item.title
    portfolio_item_display.short_description = 'Portfolio Item'
    portfolio_item_display.admin_order_field = 'portfolio_item__title'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />', 
                obj.image.url
            )
        return "—"
    image_preview.short_description = 'Preview'
    
    def image_preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 300px; max-width: 100%;" />', 
                obj.image.url
            )
        return "—"
    image_preview_large.short_description = 'Large Preview'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('portfolio_item')