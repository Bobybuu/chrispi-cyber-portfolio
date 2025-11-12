#portfolio/models.py
import uuid
import json
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.utils import timezone

User = get_user_model()


class PortfolioCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, max_length=110)
    description = models.TextField(blank=True, help_text="Brief description of the category")
    order = models.PositiveIntegerField(default=0, help_text="Display order (lower numbers first)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Portfolio categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def published_items_count(self):
        return self.portfolio_items.filter(is_published=True).count()


class PortfolioItem(models.Model):
    CATEGORY_CHOICES = [
        ('cybersecurity', 'Cybersecurity Case Studies'),
        ('writing', 'Writing Samples'),
        ('publications', 'Publications'),
        ('consulting', 'Consulting Projects'),
        ('strategy', 'Strategy & Planning'),
        ('implementation', 'Implementation Projects'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=220)
    category = models.ForeignKey(
        PortfolioCategory, 
        on_delete=models.PROTECT, 
        related_name='portfolio_items',
        help_text="Main category for this portfolio item"
    )
    secondary_categories = models.ManyToManyField(
        PortfolioCategory, 
        related_name='secondary_portfolio_items',
        blank=True,
        help_text="Additional categories for this item"
    )
    
    # Content
    summary = models.TextField(help_text="Brief summary/description")
    content = models.TextField(help_text="Detailed content (HTML allowed)", blank=True)
    sanitized_content = models.TextField(editable=False, blank=True)
    
    # Media & Links
    featured_image = models.ImageField(upload_to='portfolio/featured/', null=True, blank=True)
    link = models.URLField(blank=True, help_text="External link to project/demo")
    client = models.CharField(max_length=200, blank=True, help_text="Client name (if applicable)")
    
    # Project metadata
    project_date = models.DateField(help_text="When the project was completed")
    duration = models.CharField(max_length=50, blank=True, help_text="Project duration (e.g., 3 months)")
    technologies = models.JSONField(
        default=list, 
        blank=True,
        help_text="List of technologies used (stored as JSON array)"
    )
    
    # Publication status
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False, help_text="Show in featured section")
    
    # Metadata
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO description")
    metadata = models.JSONField(
        default=dict, 
        blank=True,
        help_text="Additional metadata (stored as JSON object)"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-project_date', '-created_at']
        indexes = [
            models.Index(fields=['is_published', 'is_featured', 'project_date']),
            models.Index(fields=['slug']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Generate slug if not provided
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Sanitize HTML content if provided
        if self.content:
            import bleach
            allowed_tags = [
                'p', 'br', 'strong', 'em', 'u', 's', 'ul', 'ol', 'li',
                'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'pre',
                'code', 'a', 'img', 'div', 'span', 'table', 'thead', 'tbody',
                'tr', 'th', 'td'
            ]
            allowed_attributes = {
                'a': ['href', 'title', 'target', 'rel'],
                'img': ['src', 'alt', 'title', 'width', 'height', 'class'],
                'div': ['class'],
                'span': ['class'],
                'code': ['class'],
                'pre': ['class'],
                'table': ['class', 'border'],
                'th': ['colspan', 'rowspan'],
                'td': ['colspan', 'rowspan'],
            }
            
            self.sanitized_content = bleach.clean(
                self.content,
                tags=allowed_tags,
                attributes=allowed_attributes,
                strip=True
            )
        
        # Auto-generate meta description from summary if not provided
        if not self.meta_description and self.summary:
            self.meta_description = self.summary[:160]
        
        # Ensure technologies is a list
        if isinstance(self.technologies, str):
            try:
                self.technologies = json.loads(self.technologies)
            except json.JSONDecodeError:
                self.technologies = [tech.strip() for tech in self.technologies.split(',')]
        
        super().save(*args, **kwargs)

    @property
    def display_date(self):
        """Formatted project date for display"""
        return self.project_date.strftime('%B %Y')

    @property
    def technologies_list(self):
        """Get technologies as a list if stored as string"""
        if isinstance(self.technologies, str):
            try:
                return json.loads(self.technologies)
            except json.JSONDecodeError:
                return [tech.strip() for tech in self.technologies.split(',')]
        return self.technologies or []

    @property
    def is_recent(self):
        """Check if the project is from the last 6 months"""
        six_months_ago = timezone.now().date() - timezone.timedelta(days=180)
        return self.project_date >= six_months_ago


class PortfolioImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    portfolio_item = models.ForeignKey(
        PortfolioItem, 
        on_delete=models.CASCADE, 
        related_name='images'
    )
    image = models.ImageField(upload_to='portfolio/images/')
    caption = models.CharField(max_length=200, blank=True)
    alt_text = models.CharField(max_length=200, blank=True, help_text="Alternative text for accessibility")
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    is_featured = models.BooleanField(default=False, help_text="Use as featured image for the item")
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['portfolio_item', 'order', 'created_at']

    def __str__(self):
        return f"Image for {self.portfolio_item.title}"

    def save(self, *args, **kwargs):
        # If this is set as featured, unset others for the same portfolio item
        if self.is_featured:
            PortfolioImage.objects.filter(
                portfolio_item=self.portfolio_item, 
                is_featured=True
            ).update(is_featured=False)
        super().save(*args, **kwargs)