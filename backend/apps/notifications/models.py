"""
Notification models for Respond IO Alternate Interface.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import uuid


class Notification(models.Model):
    """
    Notification model for in-app notifications and alerts.
    """
    
    class NotificationType(models.TextChoices):
        MESSAGE = 'message', _('New Message')
        ASSIGNMENT = 'assignment', _('Customer Assignment')
        MENTION = 'mention', _('User Mention')
        COMMENT = 'comment', _('Internal Comment')
        FILE_SHARE = 'file_share', _('File Share')
        SYSTEM = 'system', _('System Notification')
        REMINDER = 'reminder', _('Reminder')
        WARNING = 'warning', _('Warning')
        ERROR = 'error', _('Error')
    
    class Priority(models.TextChoices):
        LOW = 'low', _('Low')
        NORMAL = 'normal', _('Normal')
        HIGH = 'high', _('High')
        URGENT = 'urgent', _('Urgent')
    
    class Status(models.TextChoices):
        PENDING = 'pending', _('Pending')
        SENT = 'sent', _('Sent')
        DELIVERED = 'delivered', _('Delivered')
        READ = 'read', _('Read')
        FAILED = 'failed', _('Failed')
    
    # Core fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text=_('User receiving the notification')
    )
    
    # Notification content
    notification_type = models.CharField(
        max_length=15,
        choices=NotificationType.choices,
        help_text=_('Type of notification')
    )
    title = models.CharField(
        _('title'),
        max_length=200,
        help_text=_('Notification title')
    )
    message = models.TextField(
        _('message'),
        help_text=_('Notification message content')
    )
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.NORMAL,
        help_text=_('Notification priority level')
    )
    
    # Status and delivery
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        help_text=_('Notification delivery status')
    )
    is_read = models.BooleanField(
        _('read'),
        default=False,
        help_text=_('Whether notification has been read')
    )
    read_at = models.DateTimeField(
        _('read at'),
        null=True,
        blank=True,
        help_text=_('When notification was marked as read')
    )
    
    # Related object (generic foreign key)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text=_('Type of related object')
    )
    object_id = models.UUIDField(
        null=True,
        blank=True,
        help_text=_('ID of related object')
    )
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Action and navigation
    action_url = models.CharField(
        _('action URL'),
        max_length=500,
        blank=True,
        help_text=_('URL to navigate to when notification is clicked')
    )
    action_data = models.JSONField(
        _('action data'),
        default=dict,
        blank=True,
        help_text=_('Additional data for notification actions')
    )
    
    # Sender information
    sender = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sent_notifications',
        help_text=_('User who triggered the notification')
    )
    
    # Delivery tracking
    in_app_delivered = models.BooleanField(
        _('in-app delivered'),
        default=False,
        help_text=_('Whether in-app notification was delivered')
    )
    email_delivered = models.BooleanField(
        _('email delivered'),
        default=False,
        help_text=_('Whether email notification was delivered')
    )
    push_delivered = models.BooleanField(
        _('push delivered'),
        default=False,
        help_text=_('Whether push notification was delivered')
    )
    
    # Expiration and grouping
    expires_at = models.DateTimeField(
        _('expires at'),
        null=True,
        blank=True,
        help_text=_('When notification should be automatically removed')
    )
    group_key = models.CharField(
        _('group key'),
        max_length=100,
        blank=True,
        help_text=_('Key for grouping similar notifications')
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    scheduled_for = models.DateTimeField(
        _('scheduled for'),
        null=True,
        blank=True,
        help_text=_('When notification should be sent (for scheduled notifications)')
    )
    sent_at = models.DateTimeField(
        _('sent at'),
        null=True,
        blank=True,
        help_text=_('When notification was actually sent')
    )
    
    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', 'is_read', 'created_at']),
            models.Index(fields=['notification_type', 'priority']),
            models.Index(fields=['status', 'scheduled_for']),
            models.Index(fields=['group_key', 'recipient']),
            models.Index(fields=['expires_at']),
            models.Index(fields=['content_type', 'object_id']),
        ]
    
    def __str__(self):
        return f"{self.title} → {self.recipient.full_name}"
    
    @property
    def is_expired(self):
        """Check if notification has expired."""
        if not self.expires_at:
            return False
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    @property
    def is_high_priority(self):
        """Check if notification is high or urgent priority."""
        return self.priority in [self.Priority.HIGH, self.Priority.URGENT]
    
    @property
    def is_scheduled(self):
        """Check if notification is scheduled for future delivery."""
        if not self.scheduled_for:
            return False
        from django.utils import timezone
        return self.scheduled_for > timezone.now()
    
    def mark_as_read(self):
        """Mark notification as read."""
        from django.utils import timezone
        
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.status = self.Status.READ
            self.save(update_fields=['is_read', 'read_at', 'status', 'updated_at'])
    
    def mark_as_delivered(self, delivery_method='in_app'):
        """Mark notification as delivered via specific method."""
        from django.utils import timezone
        
        if delivery_method == 'in_app':
            self.in_app_delivered = True
        elif delivery_method == 'email':
            self.email_delivered = True
        elif delivery_method == 'push':
            self.push_delivered = True
        
        self.status = self.Status.DELIVERED
        self.sent_at = timezone.now()
        self.save(update_fields=[
            f'{delivery_method}_delivered', 'status', 'sent_at', 'updated_at'
        ])
    
    def mark_as_failed(self):
        """Mark notification delivery as failed."""
        self.status = self.Status.FAILED
        self.save(update_fields=['status', 'updated_at'])
    
    @classmethod
    def create_notification(cls, recipient, notification_type, title, message, **kwargs):
        """Create a new notification with standard fields."""
        return cls.objects.create(
            recipient=recipient,
            notification_type=notification_type,
            title=title,
            message=message,
            **kwargs
        )
    
    @classmethod
    def cleanup_expired(cls):
        """Remove expired notifications."""
        from django.utils import timezone
        cls.objects.filter(
            expires_at__lt=timezone.now()
        ).delete()


class NotificationPreference(models.Model):
    """
    User preferences for notification delivery and types.
    """
    
    class DeliveryMethod(models.TextChoices):
        IN_APP = 'in_app', _('In-App')
        EMAIL = 'email', _('Email')
        PUSH = 'push', _('Push Notification')
        SMS = 'sms', _('SMS')
    
    # Core fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name='notification_preferences',
        help_text=_('User these preferences belong to')
    )
    
    # Notification type settings
    notification_type = models.CharField(
        max_length=15,
        choices=Notification.NotificationType.choices,
        help_text=_('Type of notification')
    )
    delivery_method = models.CharField(
        max_length=10,
        choices=DeliveryMethod.choices,
        help_text=_('Delivery method for this notification type')
    )
    
    # Preference settings
    is_enabled = models.BooleanField(
        _('enabled'),
        default=True,
        help_text=_('Whether this notification type is enabled')
    )
    minimum_priority = models.CharField(
        _('minimum priority'),
        max_length=10,
        choices=Notification.Priority.choices,
        default=Notification.Priority.NORMAL,
        help_text=_('Minimum priority level to receive notifications')
    )
    
    # Timing preferences
    quiet_hours_start = models.TimeField(
        _('quiet hours start'),
        null=True,
        blank=True,
        help_text=_('Start of quiet hours (no notifications)')
    )
    quiet_hours_end = models.TimeField(
        _('quiet hours end'),
        null=True,
        blank=True,
        help_text=_('End of quiet hours')
    )
    weekend_enabled = models.BooleanField(
        _('weekend notifications'),
        default=True,
        help_text=_('Whether to receive notifications on weekends')
    )
    
    # Frequency control
    digest_frequency = models.CharField(
        _('digest frequency'),
        max_length=20,
        choices=[
            ('immediate', _('Immediate')),
            ('hourly', _('Hourly')),
            ('daily', _('Daily')),
            ('weekly', _('Weekly')),
            ('disabled', _('Disabled')),
        ],
        default='immediate',
        help_text=_('How often to send digest notifications')
    )
    max_per_day = models.PositiveIntegerField(
        _('max per day'),
        null=True,
        blank=True,
        help_text=_('Maximum notifications per day (null = unlimited)')
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Notification Preference')
        verbose_name_plural = _('Notification Preferences')
        unique_together = ['user', 'notification_type', 'delivery_method']
        ordering = ['user', 'notification_type', 'delivery_method']
        indexes = [
            models.Index(fields=['user', 'is_enabled']),
            models.Index(fields=['notification_type', 'delivery_method']),
        ]
    
    def __str__(self):
        status = "enabled" if self.is_enabled else "disabled"
        return f"{self.user.full_name} - {self.get_notification_type_display()} via {self.get_delivery_method_display()} ({status})"
    
    @property
    def is_in_quiet_hours(self):
        """Check if current time is within user's quiet hours."""
        if not (self.quiet_hours_start and self.quiet_hours_end):
            return False
        
        from django.utils import timezone
        now = timezone.now().time()
        
        if self.quiet_hours_start <= self.quiet_hours_end:
            # Same day quiet hours (e.g., 22:00 - 08:00 next day)
            return self.quiet_hours_start <= now <= self.quiet_hours_end
        else:
            # Cross-midnight quiet hours (e.g., 22:00 - 08:00 next day)
            return now >= self.quiet_hours_start or now <= self.quiet_hours_end
    
    @property
    def is_weekend_and_disabled(self):
        """Check if it's weekend and weekend notifications are disabled."""
        if self.weekend_enabled:
            return False
        
        from django.utils import timezone
        return timezone.now().weekday() >= 5  # Saturday = 5, Sunday = 6
    
    def should_send_notification(self, notification):
        """Check if notification should be sent based on preferences."""
        # Check if preference is enabled
        if not self.is_enabled:
            return False
        
        # Check priority level
        priority_order = {
            Notification.Priority.LOW: 0,
            Notification.Priority.NORMAL: 1,
            Notification.Priority.HIGH: 2,
            Notification.Priority.URGENT: 3,
        }
        
        if priority_order[notification.priority] < priority_order[self.minimum_priority]:
            return False
        
        # Check quiet hours
        if self.is_in_quiet_hours and notification.priority != Notification.Priority.URGENT:
            return False
        
        # Check weekend setting
        if self.is_weekend_and_disabled and notification.priority != Notification.Priority.URGENT:
            return False
        
        # Check daily limit
        if self.max_per_day:
            from django.utils import timezone
            today = timezone.now().date()
            today_count = Notification.objects.filter(
                recipient=self.user,
                notification_type=self.notification_type,
                created_at__date=today
            ).count()
            
            if today_count >= self.max_per_day:
                return False
        
        return True
    
    @classmethod
    def get_user_preference(cls, user, notification_type, delivery_method):
        """Get user preference for specific notification type and delivery method."""
        try:
            return cls.objects.get(
                user=user,
                notification_type=notification_type,
                delivery_method=delivery_method
            )
        except cls.DoesNotExist:
            # Return default preference
            return cls(
                user=user,
                notification_type=notification_type,
                delivery_method=delivery_method,
                is_enabled=True,
                minimum_priority=Notification.Priority.NORMAL
            )
    
    @classmethod
    def create_default_preferences(cls, user):
        """Create default notification preferences for a new user."""
        default_preferences = [
            # Messages - In-app and email
            (Notification.NotificationType.MESSAGE, cls.DeliveryMethod.IN_APP, True),
            (Notification.NotificationType.MESSAGE, cls.DeliveryMethod.EMAIL, True),
            
            # Assignments - In-app and email
            (Notification.NotificationType.ASSIGNMENT, cls.DeliveryMethod.IN_APP, True),
            (Notification.NotificationType.ASSIGNMENT, cls.DeliveryMethod.EMAIL, True),
            
            # Mentions - In-app, email, and push
            (Notification.NotificationType.MENTION, cls.DeliveryMethod.IN_APP, True),
            (Notification.NotificationType.MENTION, cls.DeliveryMethod.EMAIL, True),
            (Notification.NotificationType.MENTION, cls.DeliveryMethod.PUSH, True),
            
            # Comments - In-app only
            (Notification.NotificationType.COMMENT, cls.DeliveryMethod.IN_APP, True),
            (Notification.NotificationType.COMMENT, cls.DeliveryMethod.EMAIL, False),
            
            # File shares - In-app and email
            (Notification.NotificationType.FILE_SHARE, cls.DeliveryMethod.IN_APP, True),
            (Notification.NotificationType.FILE_SHARE, cls.DeliveryMethod.EMAIL, True),
            
            # System notifications - In-app only
            (Notification.NotificationType.SYSTEM, cls.DeliveryMethod.IN_APP, True),
            (Notification.NotificationType.SYSTEM, cls.DeliveryMethod.EMAIL, False),
        ]
        
        preferences = []
        for notification_type, delivery_method, is_enabled in default_preferences:
            pref, created = cls.objects.get_or_create(
                user=user,
                notification_type=notification_type,
                delivery_method=delivery_method,
                defaults={'is_enabled': is_enabled}
            )
            preferences.append(pref)
        
        return preferences


class NotificationDigest(models.Model):
    """
    Notification digest for batching notifications.
    """
    
    class DigestType(models.TextChoices):
        HOURLY = 'hourly', _('Hourly')
        DAILY = 'daily', _('Daily')
        WEEKLY = 'weekly', _('Weekly')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name='notification_digests',
        help_text=_('User receiving the digest')
    )
    
    # Digest settings
    digest_type = models.CharField(
        max_length=10,
        choices=DigestType.choices,
        help_text=_('Type of digest')
    )
    delivery_method = models.CharField(
        max_length=10,
        choices=NotificationPreference.DeliveryMethod.choices,
        help_text=_('How digest will be delivered')
    )
    
    # Digest content
    notification_count = models.PositiveIntegerField(
        _('notification count'),
        default=0,
        help_text=_('Number of notifications in digest')
    )
    digest_content = models.JSONField(
        _('digest content'),
        default=dict,
        help_text=_('Aggregated notification content')
    )
    
    # Status
    is_sent = models.BooleanField(
        _('sent'),
        default=False,
        help_text=_('Whether digest has been sent')
    )
    sent_at = models.DateTimeField(
        _('sent at'),
        null=True,
        blank=True,
        help_text=_('When digest was sent')
    )
    
    # Time period
    period_start = models.DateTimeField(
        _('period start'),
        help_text=_('Start of digest period')
    )
    period_end = models.DateTimeField(
        _('period end'),
        help_text=_('End of digest period')
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('Notification Digest')
        verbose_name_plural = _('Notification Digests')
        ordering = ['-period_end']
        unique_together = ['user', 'digest_type', 'delivery_method', 'period_start']
        indexes = [
            models.Index(fields=['user', 'is_sent']),
            models.Index(fields=['digest_type', 'period_end']),
            models.Index(fields=['is_sent', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_digest_type_display()} digest for {self.user.full_name} ({self.notification_count} notifications)"
    
    def add_notification(self, notification):
        """Add notification to digest."""
        self.notification_count += 1
        
        # Update digest content structure
        if 'notifications' not in self.digest_content:
            self.digest_content['notifications'] = []
        
        self.digest_content['notifications'].append({
            'id': str(notification.id),
            'type': notification.notification_type,
            'title': notification.title,
            'message': notification.message,
            'priority': notification.priority,
            'created_at': notification.created_at.isoformat(),
        })
        
        # Update summary by type
        if 'summary' not in self.digest_content:
            self.digest_content['summary'] = {}
        
        type_key = notification.notification_type
        if type_key not in self.digest_content['summary']:
            self.digest_content['summary'][type_key] = 0
        self.digest_content['summary'][type_key] += 1
        
        self.save(update_fields=['notification_count', 'digest_content', 'updated_at'])
    
    def mark_as_sent(self):
        """Mark digest as sent."""
        from django.utils import timezone
        self.is_sent = True
        self.sent_at = timezone.now()
        self.save(update_fields=['is_sent', 'sent_at', 'updated_at']) 