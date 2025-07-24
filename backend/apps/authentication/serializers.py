"""
Authentication serializers for JWT-based authentication system.
"""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .models import User, LoginAttempt
import uuid


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer with additional user data and security checks.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Use email instead of username
        self.fields['email'] = serializers.EmailField()
        self.fields.pop('username', None)

    def validate(self, attrs):
        """Custom validation with security checks and login attempt tracking."""
        email = attrs.get('email')
        password = attrs.get('password')
        
        # Get client IP for logging
        request = self.context.get('request')
        ip_address = self.get_client_ip(request) if request else '127.0.0.1'
        user_agent = request.META.get('HTTP_USER_AGENT', '') if request else ''
        
        if not email or not password:
            self.log_login_attempt(email, ip_address, user_agent, LoginAttempt.Status.FAILED, 'Missing credentials')
            raise serializers.ValidationError(_('Email and password are required.'))
        
        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            self.log_login_attempt(email, ip_address, user_agent, LoginAttempt.Status.FAILED, 'User not found')
            raise serializers.ValidationError(_('Invalid email or password.'))
        
        # Check if account is locked
        if user.is_account_locked():
            self.log_login_attempt(email, ip_address, user_agent, LoginAttempt.Status.BLOCKED, 'Account locked')
            raise serializers.ValidationError(_('Account is temporarily locked due to multiple failed login attempts.'))
        
        # Check if user is active
        if not user.is_active:
            self.log_login_attempt(email, ip_address, user_agent, LoginAttempt.Status.FAILED, 'Account disabled')
            raise serializers.ValidationError(_('Account is disabled.'))
        
        # Authenticate user
        user = authenticate(request=request, username=email, password=password)
        if not user:
            # Increment failed login attempts
            existing_user = User.objects.get(email=email)
            existing_user.failed_login_attempts += 1
            if existing_user.failed_login_attempts >= 5:
                existing_user.lock_account(duration_minutes=30)
                self.log_login_attempt(email, ip_address, user_agent, LoginAttempt.Status.BLOCKED, 'Too many failed attempts')
                raise serializers.ValidationError(_('Account locked due to multiple failed login attempts.'))
            
            existing_user.save(update_fields=['failed_login_attempts'])
            self.log_login_attempt(email, ip_address, user_agent, LoginAttempt.Status.FAILED, 'Invalid password')
            raise serializers.ValidationError(_('Invalid email or password.'))
        
        # Success - log successful login
        self.log_login_attempt(email, ip_address, user_agent, LoginAttempt.Status.SUCCESS, '')
        
        # Update user login info
        user.last_login = timezone.now()
        user.last_login_ip = ip_address
        user.failed_login_attempts = 0  # Reset failed attempts
        user.save(update_fields=['last_login', 'last_login_ip', 'failed_login_attempts'])
        
        # Get token data
        refresh = self.get_token(user)
        
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': str(user.id),
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': user.full_name,
                'role': user.role,
                'designation': user.designation,
                'password_change_required': user.password_change_required,
                'last_login': user.last_login.isoformat() if user.last_login else None,
            }
        }
    
    @classmethod
    def get_token(cls, user):
        """Get JWT token with custom claims."""
        token = super().get_token(user)
        
        # Add custom claims
        token['email'] = user.email
        token['role'] = user.role
        token['full_name'] = user.full_name
        token['user_id'] = str(user.id)
        
        return token
    
    def get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def log_login_attempt(self, email, ip_address, user_agent, status, failure_reason=''):
        """Log login attempt for security monitoring."""
        LoginAttempt.objects.create(
            email=email,
            ip_address=ip_address,
            user_agent=user_agent,
            status=status,
            failure_reason=failure_reason
        )


class UserSerializer(serializers.ModelSerializer):
    """
    User serializer for profile data.
    """
    full_name = serializers.ReadOnlyField()
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 'full_name',
            'role', 'role_display', 'designation', 'respond_io_account_id',
            'password_change_required', 'last_login', 'date_joined', 'is_active'
        ]
        read_only_fields = [
            'id', 'email', 'username', 'last_login', 'date_joined', 'role'
        ]


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for password change functionality.
    """
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    
    def validate_current_password(self, value):
        """Validate current password."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(_('Current password is incorrect.'))
        return value
    
    def validate_new_password(self, value):
        """Validate new password."""
        user = self.context['request'].user
        try:
            validate_password(value, user)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value
    
    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': _('Password confirmation does not match.')
            })
        
        # Check if new password is different from current
        user = self.context['request'].user
        if user.check_password(attrs['new_password']):
            raise serializers.ValidationError({
                'new_password': _('New password must be different from current password.')
            })
        
        return attrs
    
    def save(self):
        """Change user password."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.password_change_required = False
        user.password_last_changed = timezone.now()
        user.save(update_fields=['password', 'password_change_required', 'password_last_changed'])
        return user


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile information.
    """
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'designation']
    
    def validate_first_name(self, value):
        """Validate first name."""
        if not value or not value.strip():
            raise serializers.ValidationError(_('First name is required.'))
        return value.strip()
    
    def validate_last_name(self, value):
        """Validate last name."""
        if not value or not value.strip():
            raise serializers.ValidationError(_('Last name is required.'))
        return value.strip()


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new users (admin only).
    """
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'username', 'first_name', 'last_name', 'role',
            'designation', 'respond_io_account_id', 'password', 'confirm_password'
        ]
    
    def validate_email(self, value):
        """Validate email uniqueness."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(_('User with this email already exists.'))
        return value
    
    def validate_username(self, value):
        """Validate username uniqueness."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(_('User with this username already exists.'))
        return value
    
    def validate_password(self, value):
        """Validate password strength."""
        try:
            validate_password(value)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value
    
    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({
                'confirm_password': _('Password confirmation does not match.')
            })
        attrs.pop('confirm_password')
        return attrs
    
    def create(self, validated_data):
        """Create new user with hashed password."""
        password = validated_data.pop('password')
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class LoginAttemptSerializer(serializers.ModelSerializer):
    """
    Serializer for login attempt logs (admin only).
    """
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = LoginAttempt
        fields = [
            'id', 'email', 'ip_address', 'user_agent', 'status', 'status_display',
            'failure_reason', 'created_at'
        ] 