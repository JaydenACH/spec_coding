"""
Django admin configuration for authentication models.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from .models import User, UserSession, LoginAttempt


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom user admin interface.
    """
    list_display = [
        'email', 'first_name', 'last_name', 'role', 'designation',
        'is_active', 'last_login', 'password_change_required'
    ]
    list_filter = [
        'role', 'is_active', 'password_change_required',
        'date_joined', 'last_login'
    ]
    search_fields = ['email', 'first_name', 'last_name', 'username']
    ordering = ['email']
    
    fieldsets = (
        (None, {
            'fields': ('email', 'username', 'password')
        }),
        (_('Personal Info'), {
            'fields': ('first_name', 'last_name', 'designation')
        }),
        (_('Role & Permissions'), {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Respond.IO Integration'), {
            'fields': ('respond_io_account_id',)
        }),
        (_('Security'), {
            'fields': (
                'password_change_required', 'password_last_changed',
                'failed_login_attempts', 'account_locked_until', 'last_login_ip'
            )
        }),
        (_('Important Dates'), {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'username', 'first_name', 'last_name',
                'role', 'designation', 'password1', 'password2'
            ),
        }),
    )
    
    readonly_fields = [
        'last_login', 'date_joined', 'password_last_changed',
        'failed_login_attempts', 'last_login_ip'
    ]
    
    actions = ['unlock_accounts', 'force_password_change', 'activate_users', 'deactivate_users']
    
    def unlock_accounts(self, request, queryset):
        """Unlock selected user accounts."""
        count = 0
        for user in queryset:
            if user.is_account_locked():
                user.unlock_account()
                count += 1
        
        self.message_user(
            request,
            f'Unlocked {count} user accounts.'
        )
    unlock_accounts.short_description = _('Unlock selected accounts')
    
    def force_password_change(self, request, queryset):
        """Force password change for selected users."""
        count = queryset.update(password_change_required=True)
        self.message_user(
            request,
            f'Password change required for {count} users.'
        )
    force_password_change.short_description = _('Force password change')
    
    def activate_users(self, request, queryset):
        """Activate selected users."""
        count = queryset.update(is_active=True)
        self.message_user(
            request,
            f'Activated {count} users.'
        )
    activate_users.short_description = _('Activate selected users')
    
    def deactivate_users(self, request, queryset):
        """Deactivate selected users."""
        count = queryset.update(is_active=False)
        self.message_user(
            request,
            f'Deactivated {count} users.'
        )
    deactivate_users.short_description = _('Deactivate selected users')


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """
    User session admin interface.
    """
    list_display = [
        'user', 'ip_address', 'is_active', 'created_at', 'last_activity'
    ]
    list_filter = ['is_active', 'created_at', 'last_activity']
    search_fields = ['user__email', 'ip_address', 'user_agent']
    readonly_fields = ['created_at', 'last_activity']
    ordering = ['-last_activity']
    
    actions = ['deactivate_sessions']
    
    def deactivate_sessions(self, request, queryset):
        """Deactivate selected sessions."""
        count = queryset.update(is_active=False)
        self.message_user(
            request,
            f'Deactivated {count} sessions.'
        )
    deactivate_sessions.short_description = _('Deactivate selected sessions')
    
    def has_add_permission(self, request):
        """Disable adding sessions through admin."""
        return False


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    """
    Login attempt admin interface.
    """
    list_display = [
        'email', 'status', 'ip_address', 'failure_reason', 'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['email', 'ip_address', 'failure_reason']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        """Disable adding login attempts through admin."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing login attempts."""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Only allow superusers to delete login attempts."""
        return request.user.is_superuser 