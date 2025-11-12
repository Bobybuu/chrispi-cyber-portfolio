import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.utils import timezone


class About(models.Model):
    """
    Singleton model for About page content
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Personal Information
    name = models.CharField(max_length=200, help_text="Full name")
    title = models.CharField(max_length=200, help_text="Professional title/headline")
    bio = models.TextField(help_text="Detailed biography (HTML allowed)")
    sanitized_bio = models.TextField(editable=False, blank=True)
    
    # Media
    photo = models.ImageField(upload_to='about/', null=True, blank=True, help_text="Professional portrait")
    profile_pdf = models.FileField(
        upload_to='about/documents/', 
        null=True, 
        blank=True, 
        help_text="Downloadable PDF profile"
    )
    
    # Contact & Social
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=100, blank=True)
    
    # Social Links (stored as JSON for flexibility)
    social_links = models.JSONField(
        default=dict,
        blank=True,
        help_text="Social media links as JSON: {'linkedin': 'url', 'twitter': 'url', ...}"
    )
    
    # Statistics/Highlights
    experience_years = models.PositiveIntegerField(default=0, help_text="Years of professional experience")
    projects_completed = models.PositiveIntegerField(default=0, help_text="Number of projects completed")
    clients_served = models.PositiveIntegerField(default=0, help_text="Number of clients served")
    
    # SEO & Metadata
    meta_title = models.CharField(max_length=60, blank=True, help_text="SEO title (max 60 chars)")
    meta_description = models.CharField(max_length=160, blank=True, help_text="SEO description (max 160 chars)")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "About"

    def __str__(self):
        return f"About - {self.name}"

    def save(self, *args, **kwargs):
        # Enforce singleton pattern by checking if any instance exists
        if not self.pk and About.objects.exists():
            # Update the existing instance instead of creating a new one
            existing = About.objects.first()
            for field in self._meta.fields:
                if field.name != 'id':  # Don't copy the ID
                    setattr(existing, field.name, getattr(self, field.name))
            existing.save()
            return
        
        # Sanitize HTML content
        if self.bio:
            import bleach
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
            
            self.sanitized_bio = bleach.clean(
                self.bio,
                tags=allowed_tags,
                attributes=allowed_attributes,
                strip=True
            )
        
        # Auto-generate meta fields if not provided
        if not self.meta_title:
            self.meta_title = f"{self.name} - {self.title}"[:60]
        
        if not self.meta_description and self.bio:
            # Create description from first part of bio
            clean_bio = self.sanitized_bio.replace('<br>', ' ').replace('</p>', ' ')
            clean_text = ' '.join(clean_bio.split())[:160]
            self.meta_description = clean_text
        
        super().save(*args, **kwargs)

    @classmethod
    def get_instance(cls):
        """Get or create the singleton instance"""
        if cls.objects.exists():
            return cls.objects.first()
        else:
            return cls.objects.create(
                name="Robert Jamngeny",
                title="ICT & Cybersecurity Specialist",
                bio="Connecting Technology, Strategy, and Storytelling for a Secure Digital Future."
            )

    @property
    def photo_url(self):
        if self.photo:
            return self.photo.url
        return None

    @property
    def profile_pdf_url(self):
        if self.profile_pdf:
            return self.profile_pdf.url
        return None

    @property
    def social_links_list(self):
        """Convert social_links JSON to a more usable format"""
        links = []
        for platform, url in self.social_links.items():
            if url:
                links.append({
                    'platform': platform,
                    'url': url,
                    'icon_name': platform.lower()  # For frontend icons
                })
        return links

class Service(models.Model):
    """
    Model for services offered
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Basic Information
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=220)
    description = models.TextField(help_text="Detailed service description")
    short_description = models.CharField(
        max_length=300, 
        blank=True,
        help_text="Brief description for cards and listings"
    )
    
    # Display
    icon_name = models.CharField(
        max_length=50, 
        blank=True,
        help_text="Icon name (e.g., 'shield', 'code', 'writing', 'strategy')"
    )
    icon_color = models.CharField(
        max_length=7, 
        default='#6366F1',
        help_text="Hex color for the icon (e.g., #6366F1)"
    )
    order = models.PositiveIntegerField(
        default=0, 
        help_text="Display order (lower numbers first)"
    )
    
    # Media
    image = models.ImageField(
        upload_to='services/', 
        null=True, 
        blank=True,
        help_text="Service image/illustration"
    )
    
    # Features/Highlights
    features = models.JSONField(
        default=list,
        blank=True,
        help_text="List of key features for this service"
    )
    
    # Pricing/CTA
    starting_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Starting price (optional)"
    )
    price_unit = models.CharField(
        max_length=20, 
        blank=True,
        default='project',
        help_text="Price unit (e.g., 'project', 'hour', 'month')"
    )
    cta_text = models.CharField(
        max_length=50, 
        default='Learn More',
        help_text="Call-to-action button text"
    )
    cta_link = models.CharField(
        max_length=200, 
        blank=True,
        help_text="CTA link (relative URL or full URL)"
    )
    
    # Publication
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(
        default=False, 
        help_text="Show in featured services section"
    )
    
    # SEO & Metadata
    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'title']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Generate slug if not provided
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Auto-generate short description from description if not provided
        if not self.short_description and self.description:
            self.short_description = self.description[:300]
        
        # Auto-generate meta fields if not provided
        if not self.meta_title:
            self.meta_title = f"{self.title} - Robert Jamngeny"[:60]
        
        if not self.meta_description and self.short_description:
            self.meta_description = self.short_description[:160]
        
        # Ensure features is a list
        if isinstance(self.features, str):
            self.features = [feature.strip() for feature in self.features.split(',')]
        
        super().save(*args, **kwargs)

    @property
    def image_url(self):
        if self.image:
            return self.image.url
        return None

    @property
    def display_price(self):
        """Formatted price for display"""
        if self.starting_price:
            return f"${self.starting_price:,.0f}+/{self.price_unit}" if self.starting_price % 1 == 0 else f"${self.starting_price:,.2f}/{self.price_unit}"
        return None

    @property
    def features_list(self):
        """Get features as a list"""
        if isinstance(self.features, str):
            return [feature.strip() for feature in self.features.split(',')]
        return self.features or []