"""
File management models for Respond IO Alternate Interface.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from django.conf import settings
import uuid
import hashlib
import mimetypes
import os


class File(models.Model):
    """
    File model for managing uploaded files with security and access control.
    """
    
    class FileType(models.TextChoices):
        IMAGE = 'image', _('Image')
        DOCUMENT = 'document', _('Document')
        AUDIO = 'audio', _('Audio')
        VIDEO = 'video', _('Video')
        ARCHIVE = 'archive', _('Archive')
        OTHER = 'other', _('Other')
    
    class UploadSource(models.TextChoices):
        USER_UPLOAD = 'user_upload', _('User Upload')
        MESSAGE_ATTACHMENT = 'message_attachment', _('Message Attachment')
        RESPOND_IO = 'respond_io', _('Respond.IO')
        SYSTEM = 'system', _('System')
    
    class VirusScanStatus(models.TextChoices):
        PENDING = 'pending', _('Pending')
        CLEAN = 'clean', _('Clean')
        INFECTED = 'infected', _('Infected')
        FAILED = 'failed', _('Scan Failed')
        SKIPPED = 'skipped', _('Skipped')
    
    # Core fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # File information
    original_filename = models.CharField(
        _('original filename'),
        max_length=255,
        help_text=_('Original name of the uploaded file')
    )
    file_path = models.CharField(
        _('file path'),
        max_length=500,
        help_text=_('Path to the stored file')
    )
    content_type = models.CharField(
        _('content type'),
        max_length=100,
        help_text=_('MIME type of the file')
    )
    file_type = models.CharField(
        max_length=10,
        choices=FileType.choices,
        help_text=_('Categorized file type')
    )
    file_size = models.PositiveIntegerField(
        _('file size'),
        help_text=_('File size in bytes')
    )
    
    # Security and validation
    file_hash = models.CharField(
        _('file hash'),
        max_length=64,
        unique=True,
        help_text=_('SHA-256 hash of file content for deduplication')
    )
    virus_scan_status = models.CharField(
        max_length=10,
        choices=VirusScanStatus.choices,
        default=VirusScanStatus.PENDING,
        help_text=_('Status of virus scan')
    )
    virus_scan_result = models.TextField(
        _('virus scan result'),
        blank=True,
        help_text=_('Detailed virus scan result')
    )
    virus_scanned_at = models.DateTimeField(
        _('virus scanned at'),
        null=True,
        blank=True,
        help_text=_('When virus scan was completed')
    )
    
    # Ownership and access
    uploaded_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_files',
        help_text=_('User who uploaded the file')
    )
    upload_source = models.CharField(
        max_length=20,
        choices=UploadSource.choices,
        default=UploadSource.USER_UPLOAD,
        help_text=_('Source of the file upload')
    )
    
    # Access control
    is_public = models.BooleanField(
        _('public access'),
        default=False,
        help_text=_('Whether file can be accessed without authentication')
    )
    access_level = models.CharField(
        _('access level'),
        max_length=20,
        choices=[
            ('private', _('Private')),
            ('team', _('Team')),
            ('organization', _('Organization')),
            ('public', _('Public')),
        ],
        default='private',
        help_text=_('Access level for the file')
    )
    
    # Metadata
    description = models.TextField(
        _('description'),
        blank=True,
        help_text=_('Optional description of the file')
    )
    tags = models.JSONField(
        _('tags'),
        default=list,
        blank=True,
        help_text=_('Tags associated with the file')
    )
    
    # Image/Video specific metadata
    width = models.PositiveIntegerField(
        _('width'),
        null=True,
        blank=True,
        help_text=_('Width in pixels for images/videos')
    )
    height = models.PositiveIntegerField(
        _('height'),
        null=True,
        blank=True,
        help_text=_('Height in pixels for images/videos')
    )
    duration = models.PositiveIntegerField(
        _('duration'),
        null=True,
        blank=True,
        help_text=_('Duration in seconds for audio/video files')
    )
    
    # Thumbnail and preview
    thumbnail_path = models.CharField(
        _('thumbnail path'),
        max_length=500,
        blank=True,
        help_text=_('Path to thumbnail image')
    )
    has_preview = models.BooleanField(
        _('has preview'),
        default=False,
        help_text=_('Whether file has a preview/thumbnail')
    )
    
    # External references
    respond_io_file_id = models.CharField(
        _('Respond.IO File ID'),
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        help_text=_('Corresponding Respond.IO file ID')
    )
    external_url = models.URLField(
        _('external URL'),
        blank=True,
        help_text=_('External URL if file is hosted elsewhere')
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    last_accessed = models.DateTimeField(
        _('last accessed'),
        null=True,
        blank=True,
        help_text=_('When file was last accessed')
    )
    
    # Expiration and retention
    expires_at = models.DateTimeField(
        _('expires at'),
        null=True,
        blank=True,
        help_text=_('When file should be automatically deleted')
    )
    retention_policy = models.CharField(
        _('retention policy'),
        max_length=50,
        blank=True,
        help_text=_('Retention policy identifier')
    )
    
    class Meta:
        verbose_name = _('File')
        verbose_name_plural = _('Files')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['uploaded_by', 'created_at']),
            models.Index(fields=['file_type', 'created_at']),
            models.Index(fields=['virus_scan_status']),
            models.Index(fields=['file_hash']),
            models.Index(fields=['respond_io_file_id']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['access_level']),
        ]
    
    def __str__(self):
        return f"{self.original_filename} ({self.file_size_human})"
    
    @property
    def file_extension(self):
        """Get file extension from filename."""
        return os.path.splitext(self.original_filename)[1].lower()
    
    @property
    def file_size_human(self):
        """Return human-readable file size."""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    @property
    def is_image(self):
        """Check if file is an image."""
        return self.file_type == self.FileType.IMAGE
    
    @property
    def is_document(self):
        """Check if file is a document."""
        return self.file_type == self.FileType.DOCUMENT
    
    @property
    def is_safe(self):
        """Check if file is safe (virus scan clean)."""
        return self.virus_scan_status == self.VirusScanStatus.CLEAN
    
    @property
    def is_expired(self):
        """Check if file has expired."""
        if not self.expires_at:
            return False
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    @property
    def download_url(self):
        """Get download URL for the file."""
        return f"/api/files/{self.id}/download/"
    
    @property
    def thumbnail_url(self):
        """Get thumbnail URL if available."""
        if self.has_preview and self.thumbnail_path:
            return f"/api/files/{self.id}/thumbnail/"
        return None
    
    def can_access(self, user=None):
        """Check if user can access this file."""
        # Public files can be accessed by anyone
        if self.is_public or self.access_level == 'public':
            return True
        
        # No user provided and file is not public
        if not user:
            return False
        
        # File owner can always access
        if self.uploaded_by == user:
            return True
        
        # Check access level
        if self.access_level == 'private':
            return False
        elif self.access_level == 'team':
            # Team members can access (same role or higher)
            return user.can_view_all_customers or self.uploaded_by
        elif self.access_level == 'organization':
            # All authenticated users can access
            return True
        
        return False
    
    def can_delete(self, user):
        """Check if user can delete this file."""
        # File owner can delete
        if self.uploaded_by == user:
            return True
        
        # System admins can delete any file
        return user.is_system_admin
    
    def generate_file_hash(self, file_content):
        """Generate SHA-256 hash of file content."""
        hash_sha256 = hashlib.sha256()
        if hasattr(file_content, 'read'):
            # File-like object
            for chunk in iter(lambda: file_content.read(4096), b""):
                hash_sha256.update(chunk)
            file_content.seek(0)  # Reset file pointer
        else:
            # Bytes content
            hash_sha256.update(file_content)
        return hash_sha256.hexdigest()
    
    def update_last_accessed(self):
        """Update last accessed timestamp."""
        from django.utils import timezone
        self.last_accessed = timezone.now()
        self.save(update_fields=['last_accessed'])
    
    def mark_virus_scan_complete(self, status, result=""):
        """Mark virus scan as complete with result."""
        from django.utils import timezone
        self.virus_scan_status = status
        self.virus_scan_result = result
        self.virus_scanned_at = timezone.now()
        self.save(update_fields=['virus_scan_status', 'virus_scan_result', 'virus_scanned_at'])
    
    def save(self, *args, **kwargs):
        """Auto-detect file type from content type."""
        if not self.file_type and self.content_type:
            if self.content_type.startswith('image/'):
                self.file_type = self.FileType.IMAGE
            elif self.content_type.startswith('audio/'):
                self.file_type = self.FileType.AUDIO
            elif self.content_type.startswith('video/'):
                self.file_type = self.FileType.VIDEO
            elif self.content_type in [
                'application/pdf', 'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'application/vnd.ms-excel',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'text/plain', 'text/csv', 'application/rtf'
            ]:
                self.file_type = self.FileType.DOCUMENT
            elif self.content_type in [
                'application/zip', 'application/x-rar-compressed',
                'application/x-tar', 'application/gzip'
            ]:
                self.file_type = self.FileType.ARCHIVE
            else:
                self.file_type = self.FileType.OTHER
        
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validate file data."""
        super().clean()
        
        # Validate file size
        max_size = getattr(settings, 'MAX_FILE_SIZE', 5 * 1024 * 1024)  # 5MB default
        if self.file_size > max_size:
            raise ValidationError({
                'file_size': _('File size exceeds maximum allowed size of {max_size} bytes.').format(max_size=max_size)
            })
        
        # Validate file extension
        allowed_extensions = getattr(settings, 'ALLOWED_FILE_TYPES', [
            'jpg', 'jpeg', 'png', 'pdf', 'doc', 'docx', 'txt'
        ])
        extension = self.file_extension.lstrip('.')
        if extension not in allowed_extensions:
            raise ValidationError({
                'original_filename': _('File type "{ext}" is not allowed.').format(ext=extension)
            })


class FileShare(models.Model):
    """
    File sharing permissions and access tracking.
    """
    
    class ShareType(models.TextChoices):
        VIEW = 'view', _('View Only')
        DOWNLOAD = 'download', _('Download')
        EDIT = 'edit', _('Edit')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.ForeignKey(
        File,
        on_delete=models.CASCADE,
        related_name='shares',
        help_text=_('File being shared')
    )
    shared_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name='created_file_shares',
        help_text=_('User who created the share')
    )
    
    # Share targets
    shared_with_user = models.ForeignKey(
        'authentication.User',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='received_file_shares',
        help_text=_('Specific user file is shared with')
    )
    shared_with_role = models.CharField(
        _('shared with role'),
        max_length=20,
        blank=True,
        choices=[
            ('basic_user', _('Basic Users')),
            ('manager', _('Managers')),
            ('system_admin', _('System Admins')),
        ],
        help_text=_('Role group file is shared with')
    )
    
    # Share permissions
    share_type = models.CharField(
        max_length=10,
        choices=ShareType.choices,
        default=ShareType.VIEW,
        help_text=_('Type of access granted')
    )
    can_reshare = models.BooleanField(
        _('can reshare'),
        default=False,
        help_text=_('Whether recipient can share with others')
    )
    
    # Share metadata
    share_message = models.TextField(
        _('share message'),
        blank=True,
        help_text=_('Optional message when sharing')
    )
    
    # Access control
    requires_password = models.BooleanField(
        _('requires password'),
        default=False,
        help_text=_('Whether access requires a password')
    )
    access_password = models.CharField(
        _('access password'),
        max_length=128,
        blank=True,
        help_text=_('Password for accessing shared file')
    )
    
    # Expiration
    expires_at = models.DateTimeField(
        _('expires at'),
        null=True,
        blank=True,
        help_text=_('When share access expires')
    )
    max_downloads = models.PositiveIntegerField(
        _('max downloads'),
        null=True,
        blank=True,
        help_text=_('Maximum number of downloads allowed')
    )
    download_count = models.PositiveIntegerField(
        _('download count'),
        default=0,
        help_text=_('Number of times file has been downloaded')
    )
    
    # Status
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_('Whether share is currently active')
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    last_accessed = models.DateTimeField(
        _('last accessed'),
        null=True,
        blank=True,
        help_text=_('When share was last accessed')
    )
    
    class Meta:
        verbose_name = _('File Share')
        verbose_name_plural = _('File Shares')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['file', 'is_active']),
            models.Index(fields=['shared_with_user', 'is_active']),
            models.Index(fields=['shared_by', 'created_at']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        target = self.shared_with_user.full_name if self.shared_with_user else f"Role: {self.shared_with_role}"
        return f"{self.file.original_filename} shared with {target}"
    
    @property
    def is_expired(self):
        """Check if share has expired."""
        if not self.expires_at:
            return False
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    @property
    def is_download_limit_reached(self):
        """Check if download limit has been reached."""
        if not self.max_downloads:
            return False
        return self.download_count >= self.max_downloads
    
    @property
    def can_access(self):
        """Check if share can currently be accessed."""
        return (
            self.is_active and 
            not self.is_expired and 
            not self.is_download_limit_reached
        )
    
    def can_user_access(self, user):
        """Check if specific user can access this share."""
        if not self.can_access:
            return False
        
        # Check user-specific share
        if self.shared_with_user:
            return self.shared_with_user == user
        
        # Check role-based share
        if self.shared_with_role:
            if self.shared_with_role == 'basic_user':
                return user.is_basic_user
            elif self.shared_with_role == 'manager':
                return user.is_manager
            elif self.shared_with_role == 'system_admin':
                return user.is_system_admin
        
        return False
    
    def record_access(self):
        """Record that share was accessed."""
        from django.utils import timezone
        self.last_accessed = timezone.now()
        self.save(update_fields=['last_accessed'])
    
    def record_download(self):
        """Record a download and increment counter."""
        from django.utils import timezone
        self.download_count += 1
        self.last_accessed = timezone.now()
        self.save(update_fields=['download_count', 'last_accessed'])
    
    def revoke(self):
        """Revoke the share access."""
        self.is_active = False
        self.save(update_fields=['is_active'])
    
    def clean(self):
        """Validate share data."""
        super().clean()
        
        # Must have either user or role target
        if not self.shared_with_user and not self.shared_with_role:
            raise ValidationError({
                'shared_with_user': _('Must specify either a user or role to share with.')
            })
        
        # Cannot have both user and role target
        if self.shared_with_user and self.shared_with_role:
            raise ValidationError({
                'shared_with_user': _('Cannot specify both user and role targets.')
            })


class FileDownloadLog(models.Model):
    """
    Log of file downloads for audit and analytics.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.ForeignKey(
        File,
        on_delete=models.CASCADE,
        related_name='download_logs',
        help_text=_('File that was downloaded')
    )
    downloaded_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='file_downloads',
        help_text=_('User who downloaded the file')
    )
    
    # Download metadata
    ip_address = models.GenericIPAddressField(
        _('IP address'),
        help_text=_('IP address of the downloader')
    )
    user_agent = models.TextField(
        _('user agent'),
        blank=True,
        help_text=_('Browser user agent string')
    )
    
    # Share context
    file_share = models.ForeignKey(
        FileShare,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='download_logs',
        help_text=_('File share used for download')
    )
    
    # Download status
    download_completed = models.BooleanField(
        _('download completed'),
        default=False,
        help_text=_('Whether download was completed successfully')
    )
    bytes_transferred = models.PositiveIntegerField(
        _('bytes transferred'),
        default=0,
        help_text=_('Number of bytes transferred')
    )
    
    # Timestamps
    started_at = models.DateTimeField(_('started at'), auto_now_add=True)
    completed_at = models.DateTimeField(
        _('completed at'),
        null=True,
        blank=True,
        help_text=_('When download was completed')
    )
    
    class Meta:
        verbose_name = _('File Download Log')
        verbose_name_plural = _('File Download Logs')
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['file', 'started_at']),
            models.Index(fields=['downloaded_by', 'started_at']),
            models.Index(fields=['ip_address', 'started_at']),
            models.Index(fields=['download_completed']),
        ]
    
    def __str__(self):
        user_info = self.downloaded_by.full_name if self.downloaded_by else f"Anonymous ({self.ip_address})"
        return f"{self.file.original_filename} downloaded by {user_info}"
    
    def mark_completed(self):
        """Mark download as completed."""
        from django.utils import timezone
        self.download_completed = True
        self.completed_at = timezone.now()
        self.bytes_transferred = self.file.file_size
        self.save(update_fields=['download_completed', 'completed_at', 'bytes_transferred']) 