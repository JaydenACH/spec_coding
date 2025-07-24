"""
Customer models for Respond IO Alternate Interface.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
import uuid
import phonenumbers
from phonenumbers import NumberParseException


class Customer(models.Model):
    """
    Customer model representing customers who interact via Respond.IO.
    """
    
    class Status(models.TextChoices):
        ASSIGNED = 'assigned', _('Assigned')
        UNASSIGNED = 'unassigned', _('Unassigned')
    
    # Core fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(
        _('phone number'),
        max_length=20,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\+[1-9]\d{1,14}$',
                message=_('Phone number must be in E.164 format (e.g., +1234567890)')
            )
        ],
        help_text=_('Phone number in E.164 format')
    )
    name = models.CharField(
        _('name'),
        max_length=100,
        blank=True,
        help_text=_('Customer display name')
    )
    
    # Status and assignment
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.UNASSIGNED,
        help_text=_('Customer assignment status')
    )
    assigned_user = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_customers',
        help_text=_('Salesperson assigned to this customer')
    )
    
    # Respond.IO integration
    respond_io_contact_id = models.CharField(
        _('Respond.IO Contact ID'),
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        help_text=_('Corresponding Respond.IO contact ID')
    )
    
    # Customer information
    email = models.EmailField(
        _('email address'),
        blank=True,
        null=True
    )
    language = models.CharField(
        _('language'),
        max_length=10,
        default='en',
        help_text=_('Customer preferred language code')
    )
    country_code = models.CharField(
        _('country code'),
        max_length=3,
        blank=True,
        help_text=_('ISO country code')
    )
    profile_picture_url = models.URLField(
        _('profile picture URL'),
        blank=True,
        help_text=_('Customer profile picture from Respond.IO')
    )
    
    # Timestamps and tracking
    first_contact_date = models.DateTimeField(
        _('first contact date'),
        auto_now_add=True,
        help_text=_('When customer first contacted us')
    )
    last_message_date = models.DateTimeField(
        _('last message date'),
        null=True,
        blank=True,
        help_text=_('When customer last sent a message')
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    # Assignment history tracking
    assignment_history = models.JSONField(
        _('assignment history'),
        default=list,
        blank=True,
        help_text=_('History of customer assignments')
    )
    
    class Meta:
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')
        ordering = ['-last_message_date', '-created_at']
        indexes = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['status', 'assigned_user']),
            models.Index(fields=['respond_io_contact_id']),
            models.Index(fields=['last_message_date']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        display_name = self.name or self.phone_number
        return f"{display_name} ({self.get_status_display()})"
    
    @property
    def display_name(self):
        """Get display name for the customer."""
        return self.name or self.phone_number
    
    @property
    def is_assigned(self):
        """Check if customer is assigned to a salesperson."""
        return self.status == self.Status.ASSIGNED and self.assigned_user is not None
    
    @property
    def formatted_phone_number(self):
        """Get formatted phone number for display."""
        try:
            parsed = phonenumbers.parse(self.phone_number, None)
            return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        except NumberParseException:
            return self.phone_number
    
    def assign_to_user(self, user, assigned_by=None):
        """Assign customer to a salesperson."""
        from django.utils import timezone
        
        # Update assignment history
        assignment_record = {
            'assigned_to': user.id if user else None,
            'assigned_by': assigned_by.id if assigned_by else None,
            'assigned_at': timezone.now().isoformat(),
            'previous_assignee': self.assigned_user.id if self.assigned_user else None,
        }
        
        if not isinstance(self.assignment_history, list):
            self.assignment_history = []
        
        self.assignment_history.append(assignment_record)
        
        # Update current assignment
        self.assigned_user = user
        self.status = self.Status.ASSIGNED if user else self.Status.UNASSIGNED
        
        self.save(update_fields=['assigned_user', 'status', 'assignment_history', 'updated_at'])
    
    def unassign(self, unassigned_by=None):
        """Unassign customer from current salesperson."""
        self.assign_to_user(None, unassigned_by)
    
    def get_assignment_count(self):
        """Get total number of times customer has been assigned."""
        return len(self.assignment_history) if isinstance(self.assignment_history, list) else 0
    
    def get_last_assignment_date(self):
        """Get the date of last assignment."""
        if not isinstance(self.assignment_history, list) or not self.assignment_history:
            return None
        
        from django.utils.dateparse import parse_datetime
        last_assignment = self.assignment_history[-1]
        return parse_datetime(last_assignment.get('assigned_at'))
    
    def clean(self):
        """Validate customer data."""
        super().clean()
        
        # Validate phone number format
        try:
            parsed = phonenumbers.parse(self.phone_number, None)
            if not phonenumbers.is_valid_number(parsed):
                from django.core.exceptions import ValidationError
                raise ValidationError({'phone_number': _('Invalid phone number.')})
        except NumberParseException:
            from django.core.exceptions import ValidationError
            raise ValidationError({'phone_number': _('Invalid phone number format.')})
        
        # Ensure consistency between status and assigned_user
        if self.status == self.Status.ASSIGNED and not self.assigned_user:
            self.status = self.Status.UNASSIGNED
        elif self.status == self.Status.UNASSIGNED and self.assigned_user:
            self.assigned_user = None


class Conversation(models.Model):
    """
    Conversation model representing chat sessions with customers.
    """
    
    class Status(models.TextChoices):
        ACTIVE = 'active', _('Active')
        CLOSED = 'closed', _('Closed')
    
    # Core fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='conversations',
        help_text=_('Customer in this conversation')
    )
    assigned_user = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='conversations',
        help_text=_('Salesperson handling this conversation')
    )
    
    # Conversation status
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.ACTIVE,
        help_text=_('Current conversation status')
    )
    
    # Respond.IO integration
    respond_io_conversation_id = models.CharField(
        _('Respond.IO Conversation ID'),
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        help_text=_('Corresponding Respond.IO conversation ID')
    )
    
    # Conversation metadata
    subject = models.CharField(
        _('subject'),
        max_length=200,
        blank=True,
        help_text=_('Conversation subject or topic')
    )
    priority = models.CharField(
        _('priority'),
        max_length=10,
        choices=[
            ('low', _('Low')),
            ('normal', _('Normal')),
            ('high', _('High')),
            ('urgent', _('Urgent')),
        ],
        default='normal'
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    last_message_at = models.DateTimeField(
        _('last message at'),
        null=True,
        blank=True,
        help_text=_('Timestamp of last message in conversation')
    )
    closed_at = models.DateTimeField(
        _('closed at'),
        null=True,
        blank=True
    )
    closed_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='closed_conversations',
        help_text=_('User who closed the conversation')
    )
    
    # Statistics
    message_count = models.PositiveIntegerField(
        _('message count'),
        default=0,
        help_text=_('Total number of messages in conversation')
    )
    internal_comment_count = models.PositiveIntegerField(
        _('internal comment count'),
        default=0,
        help_text=_('Total number of internal comments')
    )
    
    class Meta:
        verbose_name = _('Conversation')
        verbose_name_plural = _('Conversations')
        ordering = ['-last_message_at', '-created_at']
        indexes = [
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['assigned_user', 'status']),
            models.Index(fields=['respond_io_conversation_id']),
            models.Index(fields=['last_message_at']),
            models.Index(fields=['created_at']),
            models.Index(fields=['priority', 'status']),
        ]
    
    def __str__(self):
        return f"Conversation with {self.customer.display_name}"
    
    @property
    def is_active(self):
        """Check if conversation is active."""
        return self.status == self.Status.ACTIVE
    
    @property
    def duration(self):
        """Get conversation duration."""
        if self.closed_at:
            return self.closed_at - self.created_at
        else:
            from django.utils import timezone
            return timezone.now() - self.created_at
    
    @property
    def has_unread_messages(self):
        """Check if conversation has unread messages for assigned user."""
        if not self.assigned_user:
            return False
        
        from apps.messaging.models import Message
        return Message.objects.filter(
            conversation=self,
            sender_type=Message.SenderType.CUSTOMER,
            read_by_user=False
        ).exists()
    
    def close_conversation(self, closed_by=None, reason=None):
        """Close the conversation."""
        from django.utils import timezone
        
        self.status = self.Status.CLOSED
        self.closed_at = timezone.now()
        self.closed_by = closed_by
        
        self.save(update_fields=['status', 'closed_at', 'closed_by', 'updated_at'])
    
    def reopen_conversation(self):
        """Reopen a closed conversation."""
        self.status = self.Status.ACTIVE
        self.closed_at = None
        self.closed_by = None
        
        self.save(update_fields=['status', 'closed_at', 'closed_by', 'updated_at'])
    
    def update_last_message_time(self):
        """Update the last message timestamp."""
        from django.utils import timezone
        
        self.last_message_at = timezone.now()
        self.save(update_fields=['last_message_at', 'updated_at'])
    
    def increment_message_count(self):
        """Increment the message count."""
        self.message_count += 1
        self.save(update_fields=['message_count', 'updated_at'])
    
    def increment_comment_count(self):
        """Increment the internal comment count."""
        self.internal_comment_count += 1
        self.save(update_fields=['internal_comment_count', 'updated_at']) 