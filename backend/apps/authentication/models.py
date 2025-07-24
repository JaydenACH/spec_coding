"""
Authentication models for Respond IO Alternate Interface.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
import uuid


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    """
    
    class Role(models.TextChoices):
        BASIC_USER = 'basic_user', _('Basic User (Salesperson)')
        MANAGER = 'manager', _('Manager')
        SYSTEM_ADMIN = 'system_admin', _('System Admin')
    
    # Core fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.BASIC_USER,
        help_text=_('User role determining access permissions')
    )
    
    # Profile information
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)
    designation = models.CharField(
        _('designation'), 
        max_length=100, 
        blank=True,
        help_text=_('Job title or position')
    )
    
    # Respond.IO integration
    respond_io_account_id = models.CharField(
        _('Respond.IO Account ID'),
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        help_text=_('Corresponding Respond.IO user account ID')
    )
    
    # Security and account management
    password_change_required = models.BooleanField(
        _('password change required'),
        default=True,
        help_text=_('Force password change on next login')
    )
    password_last_changed = models.DateTimeField(
        _('password last changed'),
        null=True,
        blank=True
    )
    failed_login_attempts = models.PositiveIntegerField(
        _('failed login attempts'),
        default=0
    )
    account_locked_until = models.DateTimeField(
        _('account locked until'),
        null=True,
        blank=True
    )
    
    # Audit fields
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    last_login_ip = models.GenericIPAddressField(
        _('last login IP'),
        null=True,
        blank=True
    )
    
    # Use email as the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['first_name', 'last_name']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['respond_io_account_id']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    @property
    def full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def is_basic_user(self):
        """Check if user is a basic user (salesperson)."""
        return self.role == self.Role.BASIC_USER
    
    @property
    def is_manager(self):
        """Check if user is a manager."""
        return self.role == self.Role.MANAGER
    
    @property
    def is_system_admin(self):
        """Check if user is a system admin."""
        return self.role == self.Role.SYSTEM_ADMIN
    
    @property
    def can_assign_customers(self):
        """Check if user can assign customers to salespersons."""
        return self.role in [self.Role.MANAGER, self.Role.SYSTEM_ADMIN]
    
    @property
    def can_manage_users(self):
        """Check if user can manage other users."""
        return self.role == self.Role.SYSTEM_ADMIN
    
    @property
    def can_view_all_customers(self):
        """Check if user can view all customers."""
        return self.role in [self.Role.MANAGER, self.Role.SYSTEM_ADMIN]
    
    def has_respond_io_account(self):
        """Check if user has a linked Respond.IO account."""
        return bool(self.respond_io_account_id)
    
    def lock_account(self, duration_minutes=30):
        """Lock user account for specified duration."""
        from django.utils import timezone
        from datetime import timedelta
        
        self.account_locked_until = timezone.now() + timedelta(minutes=duration_minutes)
        self.save(update_fields=['account_locked_until'])
    
    def unlock_account(self):
        """Unlock user account."""
        self.account_locked_until = None
        self.failed_login_attempts = 0
        self.save(update_fields=['account_locked_until', 'failed_login_attempts'])
    
    def is_account_locked(self):
        """Check if account is currently locked."""
        from django.utils import timezone
        
        if self.account_locked_until:
            return timezone.now() < self.account_locked_until
        return False


class UserSession(models.Model):
    """
    Track user sessions for security and audit purposes.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    session_key = models.CharField(max_length=40, unique=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _('User Session')
        verbose_name_plural = _('User Sessions')
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_key']),
            models.Index(fields=['last_activity']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.ip_address}"


class LoginAttempt(models.Model):
    """
    Track login attempts for security monitoring.
    """
    
    class Status(models.TextChoices):
        SUCCESS = 'success', _('Success')
        FAILED = 'failed', _('Failed')
        BLOCKED = 'blocked', _('Blocked')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('email address'))
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    status = models.CharField(
        max_length=10,
        choices=Status.choices
    )
    failure_reason = models.CharField(
        max_length=100,
        blank=True,
        help_text=_('Reason for login failure')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Login Attempt')
        verbose_name_plural = _('Login Attempts')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email', 'status']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.email} - {self.status} - {self.created_at}" 