"""
Messaging models for Respond IO Alternate Interface.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
import uuid
import mimetypes


class Message(models.Model):
    """
    Message model representing messages in conversations.
    """
    
    class SenderType(models.TextChoices):
        CUSTOMER = 'customer', _('Customer')
        USER = 'user', _('User (Internal)')
        SYSTEM = 'system', _('System')
    
    class MessageType(models.TextChoices):
        TEXT = 'text', _('Text')
        IMAGE = 'image', _('Image')
        DOCUMENT = 'document', _('Document')
        AUDIO = 'audio', _('Audio')
        VIDEO = 'video', _('Video')
        LOCATION = 'location', _('Location')
        CONTACT = 'contact', _('Contact')
        STICKER = 'sticker', _('Sticker')
        SYSTEM = 'system', _('System Message')
    
    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        SENT = 'sent', _('Sent')
        DELIVERED = 'delivered', _('Delivered')
        READ = 'read', _('Read')
        FAILED = 'failed', _('Failed')
    
    # Core fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        'customers.Conversation',
        on_delete=models.CASCADE,
        related_name='messages',
        help_text=_('Conversation this message belongs to')
    )
    
    # Message content
    message_type = models.CharField(
        max_length=15,
        choices=MessageType.choices,
        default=MessageType.TEXT,
        help_text=_('Type of message content')
    )
    content = models.TextField(
        _('content'),
        help_text=_('Message text content')
    )
    
    # Sender information
    sender_type = models.CharField(
        max_length=10,
        choices=SenderType.choices,
        help_text=_('Type of message sender')
    )
    sender_user = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_messages',
        help_text=_('User who sent this message (if internal)')
    )
    sender_customer = models.ForeignKey(
        'customers.Customer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_messages',
        help_text=_('Customer who sent this message (if external)')
    )
    
    # Message status and delivery
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        help_text=_('Message delivery status')
    )
    read_by_user = models.BooleanField(
        _('read by user'),
        default=False,
        help_text=_('Whether assigned user has read this message')
    )
    read_at = models.DateTimeField(
        _('read at'),
        null=True,
        blank=True,
        help_text=_('When the message was marked as read')
    )
    
    # Respond.IO integration
    respond_io_message_id = models.CharField(
        _('Respond.IO Message ID'),
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        help_text=_('Corresponding Respond.IO message ID')
    )
    
    # Message metadata
    reply_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replies',
        help_text=_('Message this is replying to')
    )
    forwarded_from = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='forwards',
        help_text=_('Original message if this is forwarded')
    )
    
    # Rich content fields
    media_url = models.URLField(
        _('media URL'),
        blank=True,
        help_text=_('URL to media content (images, videos, etc.)')
    )
    thumbnail_url = models.URLField(
        _('thumbnail URL'),
        blank=True,
        help_text=_('URL to media thumbnail')
    )
    
    # Location data (for location messages)
    latitude = models.DecimalField(
        _('latitude'),
        max_digits=10,
        decimal_places=8,
        null=True,
        blank=True,
        help_text=_('Latitude for location messages')
    )
    longitude = models.DecimalField(
        _('longitude'),
        max_digits=11,
        decimal_places=8,
        null=True,
        blank=True,
        help_text=_('Longitude for location messages')
    )
    location_name = models.CharField(
        _('location name'),
        max_length=200,
        blank=True,
        help_text=_('Named location for location messages')
    )
    
    # Contact data (for contact messages)
    contact_name = models.CharField(
        _('contact name'),
        max_length=100,
        blank=True,
        help_text=_('Contact name for contact messages')
    )
    contact_phone = models.CharField(
        _('contact phone'),
        max_length=20,
        blank=True,
        help_text=_('Contact phone for contact messages')
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    sent_at = models.DateTimeField(
        _('sent at'),
        null=True,
        blank=True,
        help_text=_('When message was actually sent to Respond.IO')
    )
    
    # Edit history
    edited_at = models.DateTimeField(
        _('edited at'),
        null=True,
        blank=True,
        help_text=_('When message was last edited')
    )
    edit_count = models.PositiveIntegerField(
        _('edit count'),
        default=0,
        help_text=_('Number of times message has been edited')
    )
    
    class Meta:
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['sender_type', 'sender_user']),
            models.Index(fields=['message_type', 'status']),
            models.Index(fields=['respond_io_message_id']),
            models.Index(fields=['read_by_user', 'created_at']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        content_preview = self.content[:50] + '...' if len(self.content) > 50 else self.content
        return f"{self.get_sender_type_display()}: {content_preview}"
    
    @property
    def sender_name(self):
        """Get the display name of the message sender."""
        if self.sender_type == self.SenderType.USER and self.sender_user:
            return self.sender_user.full_name
        elif self.sender_type == self.SenderType.CUSTOMER and self.sender_customer:
            return self.sender_customer.display_name
        elif self.sender_type == self.SenderType.SYSTEM:
            return 'System'
        return 'Unknown'
    
    @property
    def is_from_customer(self):
        """Check if message is from a customer."""
        return self.sender_type == self.SenderType.CUSTOMER
    
    @property
    def is_from_user(self):
        """Check if message is from an internal user."""
        return self.sender_type == self.SenderType.USER
    
    @property
    def has_media(self):
        """Check if message has media content."""
        return self.message_type in [
            self.MessageType.IMAGE,
            self.MessageType.DOCUMENT,
            self.MessageType.AUDIO,
            self.MessageType.VIDEO
        ]
    
    @property
    def is_location_message(self):
        """Check if message is a location message."""
        return self.message_type == self.MessageType.LOCATION
    
    @property
    def is_contact_message(self):
        """Check if message is a contact message."""
        return self.message_type == self.MessageType.CONTACT
    
    def mark_as_read(self, user=None):
        """Mark message as read by user."""
        from django.utils import timezone
        
        if not self.read_by_user:
            self.read_by_user = True
            self.read_at = timezone.now()
            self.save(update_fields=['read_by_user', 'read_at', 'updated_at'])
    
    def mark_as_delivered(self):
        """Mark message as delivered."""
        if self.status in [self.Status.PENDING, self.Status.SENT]:
            self.status = self.Status.DELIVERED
            self.save(update_fields=['status', 'updated_at'])
    
    def mark_as_failed(self):
        """Mark message as failed."""
        self.status = self.Status.FAILED
        self.save(update_fields=['status', 'updated_at'])
    
    def clean(self):
        """Validate message data."""
        super().clean()
        
        # Validate sender consistency
        if self.sender_type == self.SenderType.USER and not self.sender_user:
            raise ValidationError({'sender_user': _('User sender is required for user messages.')})
        elif self.sender_type == self.SenderType.CUSTOMER and not self.sender_customer:
            raise ValidationError({'sender_customer': _('Customer sender is required for customer messages.')})
        elif self.sender_type == self.SenderType.SYSTEM and (self.sender_user or self.sender_customer):
            raise ValidationError({'sender_type': _('System messages should not have user or customer senders.')})
        
        # Validate location data
        if self.message_type == self.MessageType.LOCATION:
            if not (self.latitude and self.longitude):
                raise ValidationError({'latitude': _('Location messages must have latitude and longitude.')})
        
        # Validate contact data
        if self.message_type == self.MessageType.CONTACT:
            if not (self.contact_name and self.contact_phone):
                raise ValidationError({'contact_name': _('Contact messages must have name and phone.')})
        
        # Validate media content
        if self.has_media and not self.media_url:
            raise ValidationError({'media_url': _('Media messages must have a media URL.')})


class MessageAttachment(models.Model):
    """
    File attachments for messages.
    """
    
    class AttachmentType(models.TextChoices):
        IMAGE = 'image', _('Image')
        DOCUMENT = 'document', _('Document') 
        AUDIO = 'audio', _('Audio')
        VIDEO = 'video', _('Video')
        OTHER = 'other', _('Other')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='attachments',
        help_text=_('Message this attachment belongs to')
    )
    
    # File information
    file_name = models.CharField(
        _('file name'),
        max_length=255,
        help_text=_('Original file name')
    )
    file_size = models.PositiveIntegerField(
        _('file size'),
        help_text=_('File size in bytes')
    )
    content_type = models.CharField(
        _('content type'),
        max_length=100,
        help_text=_('MIME type of the file')
    )
    attachment_type = models.CharField(
        max_length=10,
        choices=AttachmentType.choices,
        help_text=_('Type of attachment')
    )
    
    # Storage URLs
    file_url = models.URLField(
        _('file URL'),
        help_text=_('URL to the actual file')
    )
    thumbnail_url = models.URLField(
        _('thumbnail URL'),
        blank=True,
        help_text=_('URL to file thumbnail (for images/videos)')
    )
    
    # Respond.IO integration
    respond_io_attachment_id = models.CharField(
        _('Respond.IO Attachment ID'),
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        help_text=_('Corresponding Respond.IO attachment ID')
    )
    
    # Security and validation
    is_virus_scanned = models.BooleanField(
        _('virus scanned'),
        default=False,
        help_text=_('Whether file has been scanned for viruses')
    )
    virus_scan_result = models.CharField(
        _('virus scan result'),
        max_length=50,
        blank=True,
        help_text=_('Result of virus scan (clean, infected, etc.)')
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Message Attachment')
        verbose_name_plural = _('Message Attachments')
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['message', 'attachment_type']),
            models.Index(fields=['respond_io_attachment_id']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.file_name} ({self.get_attachment_type_display()})"
    
    @property
    def file_extension(self):
        """Get file extension from filename."""
        import os
        return os.path.splitext(self.file_name)[1].lower()
    
    @property
    def is_image(self):
        """Check if attachment is an image."""
        return self.attachment_type == self.AttachmentType.IMAGE
    
    @property
    def is_document(self):
        """Check if attachment is a document."""
        return self.attachment_type == self.AttachmentType.DOCUMENT
    
    @property
    def file_size_human(self):
        """Return human-readable file size."""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"
    
    def save(self, *args, **kwargs):
        """Auto-detect attachment type from content type."""
        if not self.attachment_type and self.content_type:
            if self.content_type.startswith('image/'):
                self.attachment_type = self.AttachmentType.IMAGE
            elif self.content_type.startswith('audio/'):
                self.attachment_type = self.AttachmentType.AUDIO
            elif self.content_type.startswith('video/'):
                self.attachment_type = self.AttachmentType.VIDEO
            elif self.content_type in [
                'application/pdf', 'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'application/vnd.ms-excel',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'text/plain', 'text/csv'
            ]:
                self.attachment_type = self.AttachmentType.DOCUMENT
            else:
                self.attachment_type = self.AttachmentType.OTHER
        
        super().save(*args, **kwargs)


class InternalComment(models.Model):
    """
    Internal comments on conversations for team communication.
    """
    
    class Priority(models.TextChoices):
        LOW = 'low', _('Low')
        NORMAL = 'normal', _('Normal')
        HIGH = 'high', _('High')
        URGENT = 'urgent', _('Urgent')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        'customers.Conversation',
        on_delete=models.CASCADE,
        related_name='internal_comments',
        help_text=_('Conversation this comment belongs to')
    )
    author = models.ForeignKey(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name='internal_comments',
        help_text=_('User who wrote this comment')
    )
    
    # Comment content
    content = models.TextField(
        _('content'),
        help_text=_('Comment text content')
    )
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.NORMAL,
        help_text=_('Comment priority level')
    )
    
    # Comment metadata
    reply_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replies',
        help_text=_('Comment this is replying to')
    )
    
    # Visibility and notifications
    is_private = models.BooleanField(
        _('private comment'),
        default=False,
        help_text=_('Whether comment is visible only to managers/admins')
    )
    notify_assigned_user = models.BooleanField(
        _('notify assigned user'),
        default=True,
        help_text=_('Whether to notify the assigned user')
    )
    notify_managers = models.BooleanField(
        _('notify managers'),
        default=False,
        help_text=_('Whether to notify all managers')
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    edited_at = models.DateTimeField(
        _('edited at'),
        null=True,
        blank=True,
        help_text=_('When comment was last edited')
    )
    
    class Meta:
        verbose_name = _('Internal Comment')
        verbose_name_plural = _('Internal Comments')
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['author', 'created_at']),
            models.Index(fields=['priority', 'created_at']),
            models.Index(fields=['is_private']),
        ]
    
    def __str__(self):
        content_preview = self.content[:50] + '...' if len(self.content) > 50 else self.content
        return f"{self.author.full_name}: {content_preview}"
    
    @property
    def is_reply(self):
        """Check if this comment is a reply to another comment."""
        return self.reply_to is not None
    
    @property
    def has_mentions(self):
        """Check if comment has user mentions."""
        return self.mentions.exists()
    
    @property
    def is_high_priority(self):
        """Check if comment is high or urgent priority."""
        return self.priority in [self.Priority.HIGH, self.Priority.URGENT]
    
    def can_view(self, user):
        """Check if user can view this comment."""
        # Private comments only visible to managers/admins
        if self.is_private and not user.can_view_all_customers:
            return False
        
        # Users can always see their own comments
        if self.author == user:
            return True
        
        # Users can see comments on conversations they're assigned to
        if self.conversation.assigned_user == user:
            return True
        
        # Managers and admins can see all comments
        return user.can_view_all_customers
    
    def can_edit(self, user):
        """Check if user can edit this comment."""
        # Only author can edit, unless user is admin
        return self.author == user or user.is_system_admin


class CommentMention(models.Model):
    """
    User mentions in internal comments (@tagging).
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    comment = models.ForeignKey(
        InternalComment,
        on_delete=models.CASCADE,
        related_name='mentions',
        help_text=_('Comment containing the mention')
    )
    mentioned_user = models.ForeignKey(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name='comment_mentions',
        help_text=_('User who was mentioned')
    )
    mentioned_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name='created_mentions',
        help_text=_('User who created the mention')
    )
    
    # Mention metadata
    position_start = models.PositiveIntegerField(
        _('position start'),
        help_text=_('Start position of mention in comment text')
    )
    position_end = models.PositiveIntegerField(
        _('position end'),
        help_text=_('End position of mention in comment text')
    )
    
    # Notification status
    notification_sent = models.BooleanField(
        _('notification sent'),
        default=False,
        help_text=_('Whether notification was sent to mentioned user')
    )
    acknowledged = models.BooleanField(
        _('acknowledged'),
        default=False,
        help_text=_('Whether mentioned user has acknowledged the mention')
    )
    acknowledged_at = models.DateTimeField(
        _('acknowledged at'),
        null=True,
        blank=True,
        help_text=_('When mention was acknowledged')
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Comment Mention')
        verbose_name_plural = _('Comment Mentions')
        ordering = ['created_at']
        unique_together = ['comment', 'mentioned_user', 'position_start']
        indexes = [
            models.Index(fields=['mentioned_user', 'acknowledged']),
            models.Index(fields=['comment', 'mentioned_user']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"@{self.mentioned_user.username} in comment by {self.mentioned_by.full_name}"
    
    def acknowledge(self):
        """Mark mention as acknowledged by the mentioned user."""
        from django.utils import timezone
        
        if not self.acknowledged:
            self.acknowledged = True
            self.acknowledged_at = timezone.now()
            self.save(update_fields=['acknowledged', 'acknowledged_at'])


class TypingIndicator(models.Model):
    """
    Track typing indicators for real-time chat experience.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(
        'customers.Conversation',
        on_delete=models.CASCADE,
        related_name='typing_indicators',
        help_text=_('Conversation where typing is happening')
    )
    user = models.ForeignKey(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name='typing_indicators',
        help_text=_('User who is typing')
    )
    
    # Typing status
    is_typing = models.BooleanField(
        _('is typing'),
        default=True,
        help_text=_('Whether user is currently typing')
    )
    
    # Timestamps
    started_at = models.DateTimeField(_('started typing at'), auto_now_add=True)
    last_activity = models.DateTimeField(_('last activity'), auto_now=True)
    
    class Meta:
        verbose_name = _('Typing Indicator')
        verbose_name_plural = _('Typing Indicators')
        unique_together = ['conversation', 'user']
        indexes = [
            models.Index(fields=['conversation', 'is_typing']),
            models.Index(fields=['last_activity']),
        ]
    
    def __str__(self):
        return f"{self.user.full_name} typing in {self.conversation}"
    
    @classmethod
    def set_typing(cls, conversation, user, is_typing=True):
        """Set typing status for user in conversation."""
        indicator, created = cls.objects.get_or_create(
            conversation=conversation,
            user=user,
            defaults={'is_typing': is_typing}
        )
        
        if not created and indicator.is_typing != is_typing:
            indicator.is_typing = is_typing
            indicator.save(update_fields=['is_typing', 'last_activity'])
        
        return indicator
    
    @classmethod
    def stop_typing(cls, conversation, user):
        """Stop typing indicator for user in conversation."""
        cls.objects.filter(
            conversation=conversation,
            user=user
        ).update(is_typing=False)
    
    @classmethod
    def cleanup_old_indicators(cls, older_than_minutes=5):
        """Clean up old typing indicators."""
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_time = timezone.now() - timedelta(minutes=older_than_minutes)
        cls.objects.filter(last_activity__lt=cutoff_time).delete() 