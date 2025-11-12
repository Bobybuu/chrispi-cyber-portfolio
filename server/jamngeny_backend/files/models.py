import uuid
import os
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError

User = get_user_model()


def file_upload_path(instance, filename):
    """Generate upload path for files: files/{year}/{month}/{uuid}_{filename}"""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('files', timezone.now().strftime('%Y/%m'), filename)


class File(models.Model):
    FILE_CATEGORIES = [
        ('document', 'Document'),
        ('image', 'Image'),
        ('pdf', 'PDF'),
        ('archive', 'Archive'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # File Information
    file = models.FileField(upload_to=file_upload_path, max_length=500)
    original_filename = models.CharField(max_length=255)
    file_size = models.PositiveBigIntegerField(help_text="File size in bytes")
    mime_type = models.CharField(max_length=100)
    file_extension = models.CharField(max_length=10)
    category = models.CharField(max_length=20, choices=FILE_CATEGORIES, default='other')
    
    # Metadata
    title = models.CharField(max_length=200, blank=True, help_text="Display title")
    description = models.TextField(blank=True, help_text="File description")
    alt_text = models.TextField(blank=True, help_text="Alternative text for images")
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="Tags for categorization"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional file metadata"
    )
    
    # Permissions & Visibility
    uploaded_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='uploaded_files'
    )
    is_public = models.BooleanField(
        default=False,
        help_text="Publicly accessible without authentication"
    )
    is_featured = models.BooleanField(default=False)
    
    # Security
    is_approved = models.BooleanField(
        default=True,
        help_text="File has been approved for use"
    )
    virus_scan_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('clean', 'Clean'),
            ('infected', 'Infected'),
            ('error', 'Error'),
        ],
        default='pending'
    )
    
    # Usage Tracking
    download_count = models.PositiveIntegerField(default=0)
    last_downloaded_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['category', 'is_public', 'is_approved']),
            models.Index(fields=['uploaded_by', 'created_at']),
            models.Index(fields=['mime_type']),
        ]
        verbose_name = 'File'
        verbose_name_plural = 'Files'

    def __str__(self):
        return self.original_filename

    def save(self, *args, **kwargs):
        # Set original filename on first save
        if not self.original_filename and self.file:
            self.original_filename = os.path.basename(self.file.name)
        
        # Set file extension
        if self.file and not self.file_extension:
            self.file_extension = self.get_file_extension()
        
        # Set MIME type if not provided
        if self.file and not self.mime_type:
            self.mime_type = self.guess_mime_type()
        
        # Set file size
        if self.file and not self.file_size:
            try:
                self.file_size = self.file.size
            except (ValueError, OSError):
                self.file_size = 0
        
        # Set category based on MIME type
        if not self.category or self.category == 'other':
            self.category = self.guess_category()
        
        # Auto-generate title from filename if not provided
        if not self.title and self.original_filename:
            self.title = os.path.splitext(self.original_filename)[0]
        
        super().save(*args, **kwargs)

    def get_file_extension(self):
        """Extract file extension from filename"""
        if self.file:
            return os.path.splitext(self.file.name)[1].lower().lstrip('.')
        return ''

    def guess_mime_type(self):
        """Guess MIME type based on file extension"""
        extension_mime_map = {
            'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png',
            'gif': 'image/gif', 'webp': 'image/webp', 'svg': 'image/svg+xml',
            'pdf': 'application/pdf', 'doc': 'application/msword',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'xls': 'application/vnd.ms-excel',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'ppt': 'application/vnd.ms-powerpoint',
            'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'zip': 'application/zip', 'rar': 'application/x-rar-compressed',
            'mp3': 'audio/mpeg', 'wav': 'audio/wav', 'mp4': 'video/mp4',
            'mov': 'video/quicktime', 'avi': 'video/x-msvideo',
            'txt': 'text/plain', 'csv': 'text/csv',
        }
        return extension_mime_map.get(self.file_extension, 'application/octet-stream')

    def guess_category(self):
        """Guess file category based on MIME type"""
        mime_to_category = {
            'image/': 'image',
            'video/': 'video',
            'audio/': 'audio',
            'application/pdf': 'pdf',
            'application/zip': 'archive',
            'application/x-rar-compressed': 'archive',
            'text/': 'document',
            'application/msword': 'document',
            'application/vnd.openxmlformats-officedocument': 'document',
            'application/vnd.ms-excel': 'document',
            'application/vnd.ms-powerpoint': 'document',
        }
        
        for mime_prefix, category in mime_to_category.items():
            if self.mime_type.startswith(mime_prefix):
                return category
        
        return 'other'

    def clean(self):
        """Validate file before saving"""
        if self.file:
            # Check file size (max 50MB)
            max_size = 50 * 1024 * 1024  # 50MB
            if self.file_size > max_size:
                raise ValidationError(f"File size cannot exceed 50MB. Current size: {self.file_size} bytes")
            
            # Check allowed file types
            allowed_extensions = {
                'jpg', 'jpeg', 'png', 'gif', 'webp', 'svg',
                'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
                'txt', 'csv', 'zip', 'rar', 'mp3', 'wav', 'mp4', 'mov', 'avi'
            }
            if self.file_extension not in allowed_extensions:
                raise ValidationError(f"File type '{self.file_extension}' is not allowed.")

    @property
    def file_url(self):
        """Get file URL"""
        if self.file:
            return self.file.url
        return None

    @property
    def display_size(self):
        """Get human-readable file size"""
        if self.file_size == 0:
            return "0 B"
        
        size_names = ['B', 'KB', 'MB', 'GB']
        i = 0
        size = float(self.file_size)
        while size >= 1024 and i < len(size_names) - 1:
            size /= 1024
            i += 1
        return f"{size:.2f} {size_names[i]}"

    @property
    def is_image(self):
        """Check if file is an image"""
        return self.category == 'image'

    @property
    def is_document(self):
        """Check if file is a document"""
        return self.category in ['document', 'pdf']

    def increment_download_count(self):
        """Increment download counter"""
        self.download_count += 1
        self.last_downloaded_at = timezone.now()
        self.save(update_fields=['download_count', 'last_downloaded_at'])

    def can_access(self, user):
        """Check if user can access this file"""
        if self.is_public:
            return True
        if user.is_authenticated:
            return user.is_admin or user == self.uploaded_by
        return False


class FileUploadRequest(models.Model):
    """
    Track file upload requests for security and auditing
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Upload Information
    original_filename = models.CharField(max_length=255)
    file_size = models.PositiveBigIntegerField()
    mime_type = models.CharField(max_length=100)
    file_extension = models.CharField(max_length=10)
    
    # Security
    upload_token = models.CharField(max_length=100, unique=True)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    
    # Metadata
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    purpose = models.CharField(max_length=200, blank=True, help_text="Purpose of this upload")
    
    # Result
    resulting_file = models.OneToOneField(
        File, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='upload_request'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Upload request for {self.original_filename}"

    @property
    def is_expired(self):
        """Check if upload request has expired"""
        return timezone.now() > self.expires_at

    @property
    def is_valid(self):
        """Check if upload request is still valid"""
        return not self.is_used and not self.is_expired