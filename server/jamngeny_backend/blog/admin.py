#blog/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Article, Tag


class TagInline(admin.TabularInline):
    model = Article.tags.through
    extra = 1
    verbose_name = "Tag"
    verbose_name_plural = "Tags"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'article_count', 'created_at')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)
    readonly_fields = ('created_at',)

    def article_count(self, obj):
        return obj.articles.count()
    article_count.short_description = 'Articles'


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        'title', 
        'author_display', 
        'is_published', 
        'published_at', 
        'read_time_display',
        'tag_list',
        'created_at'
    )
    list_filter = ('is_published', 'tags', 'created_at', 'published_at')
    search_fields = ('title', 'excerpt', 'sanitized_content', 'author__email', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at', 'sanitized_content')
    date_hierarchy = 'published_at'
    inlines = [TagInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'author', 'excerpt', 'meta_description')
        }),
        ('Content', {
            'fields': ('content', 'sanitized_content', 'featured_image')
        }),
        ('Publication', {
            'fields': ('is_published', 'published_at', 'tags')
        }),
        ('Metadata', {
            'fields': ('read_time', 'created_at', 'updated_at')
        }),
    )
    
    def author_display(self, obj):
        return obj.author.email
    author_display.short_description = 'Author'
    author_display.admin_order_field = 'author__email'
    
    def read_time_display(self, obj):
        return f"{obj.read_time} min"
    read_time_display.short_description = 'Read Time'
    
    def tag_list(self, obj):
        return ", ".join(tag.name for tag in obj.tags.all()[:3])
    tag_list.short_description = 'Tags'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('author').prefetch_related('tags')
    
    def save_model(self, request, obj, form, change):
        # Auto-calculate read time if not set
        if not obj.read_time or form.changed_data and 'content' in form.changed_data:
            obj.read_time = obj.calculate_read_time()
        super().save_model(request, obj, form, change)