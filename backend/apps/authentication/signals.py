"""
Authentication signals for user management and notifications.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.utils import timezone
from .models import User, LoginAttempt, UserSession


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create default notification preferences when a new user is created."""
    if created:
        # Import here to avoid circular imports
        from apps.notifications.models import NotificationPreference
        
        # Create default notification preferences
        NotificationPreference.create_default_preferences(instance)
        
        # Log user creation
        print(f"Created user: {instance.email} with role: {instance.role}")


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log successful user login."""
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    # Create login attempt record
    LoginAttempt.objects.create(
        email=user.email,
        ip_address=ip_address,
        user_agent=user_agent,
        status=LoginAttempt.Status.SUCCESS
    )
    
    # Update user's last login IP
    user.last_login_ip = ip_address
    user.failed_login_attempts = 0  # Reset failed attempts on successful login
    user.save(update_fields=['last_login_ip', 'failed_login_attempts'])
    
    # Create user session record
    if hasattr(request, 'session'):
        UserSession.objects.create(
            user=user,
            session_key=request.session.session_key,
            ip_address=ip_address,
            user_agent=user_agent
        )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log user logout and deactivate session."""
    if user and hasattr(request, 'session'):
        # Deactivate user session
        UserSession.objects.filter(
            user=user,
            session_key=request.session.session_key
        ).update(is_active=False)


def get_client_ip(request):
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip 