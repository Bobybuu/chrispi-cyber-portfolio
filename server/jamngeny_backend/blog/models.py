# blog/models.py
import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.utils import timezone
import bleach

User = get_user_model()


class Tag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, max_length=60)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Article(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=220)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    excerpt = models.TextField(max_length=500, help_text="Brief summary of the article")
    content = models.TextField(help_text="Full article content (HTML allowed)")
    sanitized_content = models.TextField(editable=False, blank=True)
    tags = models.ManyToManyField(Tag, related_name='articles', blank=True)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True)
    read_time = models.PositiveIntegerField(help_text="Reading time in minutes", default=5)
    featured_image = models.ImageField(upload_to='articles/', null=True, blank=True)
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO description")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Generate slug if not provided
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Set published_at if publishing for the first time
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        
        # Sanitize HTML content
        if self.content:
            # Allowed HTML tags and attributes
            allowed_tags = [
                'p', 'br', 'strong', 'em', 'u', 's', 'ul', 'ol', 'li',
                'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'pre',
                'code', 'a', 'img', 'div', 'span'
            ]
            allowed_attributes = {
                'a': ['href', 'title', 'target', 'rel'],
                'img': ['src', 'alt', 'title', 'width', 'height'],
                'div': ['class'],
                'span': ['class'],
                'code': ['class'],
                'pre': ['class'],
            }
            
            self.sanitized_content = bleach.clean(
                self.content,
                tags=allowed_tags,
                attributes=allowed_attributes,
                strip=True
            )
        
        # Auto-generate meta description from excerpt if not provided
        if not self.meta_description and self.excerpt:
            self.meta_description = self.excerpt[:160]
        
        super().save(*args, **kwargs)
    
    def calculate_read_time(self):
        """Calculate read time based on content length"""
        content_to_use = self.sanitized_content if self.sanitized_content else self.content
        word_count = len(content_to_use.split())
        return max(1, round(word_count / 200))

    @property
    def is_public(self):
        return self.is_published and self.published_at <= timezone.now()