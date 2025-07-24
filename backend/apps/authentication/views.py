"""
Authentication views for JWT-based authentication system.
"""

from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin, ListModelMixin
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.contrib.auth import logout
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import User, LoginAttempt, UserSession
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserSerializer,
    PasswordChangeSerializer,
    ProfileUpdateSerializer,
    UserCreateSerializer,
    LoginAttemptSerializer
)
from .permissions import (
    IsSystemAdmin,
    IsManagerOrSystemAdmin,
    IsOwnerOrSystemAdmin,
    IsAssignedUserOrManager,
    CanViewCustomers,
    CanAssignCustomers,
    CanManageUsers
)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token obtain view with enhanced security and user data.
    """
    serializer_class = CustomTokenObtainPairSerializer
    
    @extend_schema(
        summary="Login with email and password",
        description="Authenticate user and return JWT tokens with user profile data",
        responses={
            200: OpenApiResponse(description="Login successful"),
            400: OpenApiResponse(description="Invalid credentials"),
            429: OpenApiResponse(description="Account locked due to too many failed attempts")
        }
    )
    def post(self, request, *args, **kwargs):
        """Login endpoint with security tracking."""
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Create user session record
            user_email = request.data.get('email')
            if user_email:
                try:
                    user = User.objects.get(email=user_email)
                    ip_address = self.get_client_ip(request)
                    user_agent = request.META.get('HTTP_USER_AGENT', '')
                    
                    # Create or update user session
                    session_key = request.session.session_key or request.session.create()
                    UserSession.objects.update_or_create(
                        user=user,
                        session_key=session_key,
                        defaults={
                            'ip_address': ip_address,
                            'user_agent': user_agent,
                            'is_active': True
                        }
                    )
                except User.DoesNotExist:
                    pass
        
        return response
    
    def get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom JWT token refresh view with session validation.
    """
    
    @extend_schema(
        summary="Refresh JWT access token",
        description="Get new access token using refresh token",
        responses={
            200: OpenApiResponse(description="Token refreshed successfully"),
            401: OpenApiResponse(description="Invalid refresh token")
        }
    )
    def post(self, request, *args, **kwargs):
        """Refresh token endpoint."""
        return super().post(request, *args, **kwargs)


@extend_schema(
    summary="Logout user",
    description="Logout user and blacklist refresh token",
    responses={
        200: OpenApiResponse(description="Logout successful"),
        400: OpenApiResponse(description="Invalid refresh token")
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """
    Logout view that blacklists the refresh token.
    """
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response(
                {'error': _('Refresh token is required')},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Blacklist the refresh token
        token = RefreshToken(refresh_token)
        token.blacklist()
        
        # Deactivate user session
        if hasattr(request, 'session') and request.session.session_key:
            UserSession.objects.filter(
                user=request.user,
                session_key=request.session.session_key
            ).update(is_active=False)
        
        # Django logout
        logout(request)
        
        # Invalidate all sessions for this user if requested
        if request.data.get('all_sessions'):
            UserSession.objects.filter(user=request.user, is_active=True).update(is_active=False)
        
        return Response(
            {'message': _('Logout successful')},
            status=status.HTTP_200_OK
        )
    
    except TokenError:
        return Response(
            {'error': _('Invalid refresh token')},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': _('Logout failed')},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class UserProfileViewSet(GenericViewSet, RetrieveModelMixin, UpdateModelMixin):
    """
    ViewSet for user profile management.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Return the current user."""
        return self.request.user
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'update' or self.action == 'partial_update':
            return ProfileUpdateSerializer
        elif self.action == 'change_password':
            return PasswordChangeSerializer
        return UserSerializer
    
    def dispatch(self, request, *args, **kwargs):
        # Enforce first-time password change requirement
        if (
            request.user.is_authenticated and
            getattr(request.user, 'password_change_required', False) and
            self.action != 'change_password'
        ):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied(_('You must change your password before continuing.'))
        return super().dispatch(request, *args, **kwargs)
    
    @extend_schema(
        summary="Get user profile",
        description="Retrieve current user's profile information"
    )
    def retrieve(self, request, *args, **kwargs):
        """Get current user profile."""
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Update user profile",
        description="Update current user's profile information"
    )
    def update(self, request, *args, **kwargs):
        """Update user profile."""
        return super().update(request, *args, **kwargs)
    
    @extend_schema(
        summary="Partially update user profile",
        description="Partially update current user's profile information"
    )
    def partial_update(self, request, *args, **kwargs):
        """Partially update user profile."""
        return super().partial_update(request, *args, **kwargs)
    
    @extend_schema(
        summary="Change password",
        description="Change current user's password",
        request=PasswordChangeSerializer,
        responses={
            200: OpenApiResponse(description="Password changed successfully"),
            400: OpenApiResponse(description="Validation error")
        }
    )
    @action(detail=True, methods=['post'])
    def change_password(self, request, *args, **kwargs):
        """Change user password."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(
            {'message': _('Password changed successfully')},
            status=status.HTTP_200_OK
        )


class UserManagementViewSet(ModelViewSet):
    """
    API endpoints for user management (CRUD operations).
    - List: System Admin sees all users, Manager sees basic users/managers, Basic User sees self only
    - Retrieve: Same as list
    - Create: System Admin only
    - Update/Partial Update: System Admin only
    - Destroy: System Admin only (soft delete)
    - Reset Password: System Admin only
    """
    queryset = User.objects.all()
    permission_classes = [IsSystemAdmin]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_permissions(self):
        # Only system admins can create, update, delete, reset password
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'reset_password']:
            permission_classes = [IsSystemAdmin]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.is_system_admin:
            return User.objects.all()
        elif user.is_manager:
            return User.objects.filter(role__in=[User.Role.BASIC_USER, User.Role.MANAGER])
        else:
            return User.objects.filter(id=user.id)

    @extend_schema(
        summary="List users",
        description="List users based on role permissions. System Admin sees all, Manager sees basic users/managers, Basic User sees self only."
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Retrieve user",
        description="Retrieve user details based on role permissions."
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Create user",
        description="Create a new user (System Admin only)."
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        summary="Update user",
        description="Update user details (System Admin only)."
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Partially update user",
        description="Partially update user details (System Admin only)."
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="Deactivate (soft delete) user",
        description="Deactivate a user account (System Admin only)."
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save(update_fields=['is_active'])
        return Response({'message': _('User deactivated')}, status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="Reset user password",
        description="Reset user password to a temporary password (System Admin only).",
        responses={
            200: OpenApiResponse(description="Password reset successful"),
            403: OpenApiResponse(description="Permission denied")
        }
    )
    @action(detail=True, methods=['post'])
    def reset_password(self, request, pk=None):
        if not request.user.is_system_admin:
            return Response({'error': _('Permission denied')}, status=status.HTTP_403_FORBIDDEN)
        user = self.get_object()
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits
        temp_password = ''.join(secrets.choice(alphabet) for i in range(12))
        user.set_password(temp_password)
        user.password_change_required = True
        user.password_last_changed = timezone.now()
        user.save(update_fields=['password', 'password_change_required', 'password_last_changed'])
        return Response({'message': _('Password reset successfully'), 'temporary_password': temp_password}, status=status.HTTP_200_OK)


class LoginAttemptViewSet(GenericViewSet, ListModelMixin):
    """
    ViewSet for viewing login attempts (admin only).
    """
    queryset = LoginAttempt.objects.all()
    serializer_class = LoginAttemptSerializer
    permission_classes = [IsSystemAdmin]
    
    def get_queryset(self):
        """Filter login attempts based on user role."""
        if self.request.user.is_system_admin:
            return self.queryset
        else:
            # Users can only see their own login attempts
            return self.queryset.filter(email=self.request.user.email)
    
    @extend_schema(
        summary="List login attempts",
        description="Get list of login attempts (filtered by permissions)"
    )
    def list(self, request, *args, **kwargs):
        """List login attempts."""
        return super().list(request, *args, **kwargs)


@extend_schema(
    summary="Check authentication status",
    description="Check if user is authenticated and get basic profile info"
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def auth_status(request):
    """
    Check authentication status and return user info.
    """
    user = request.user
    return Response({
        'authenticated': True,
        'user': {
            'id': str(user.id),
            'email': user.email,
            'full_name': user.full_name,
            'role': user.role,
            'password_change_required': user.password_change_required,
        }
    })


@extend_schema(
    summary="Unlock user account",
    description="Unlock a locked user account (admin only)"
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def unlock_account(request, user_id):
    """
    Unlock a user account (admin only).
    """
    if not request.user.is_system_admin:
        return Response(
            {'error': _('Permission denied')},
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        user = User.objects.get(id=user_id)
        user.unlock_account()
        
        return Response(
            {'message': _('Account unlocked successfully')},
            status=status.HTTP_200_OK
        )
    except User.DoesNotExist:
        return Response(
            {'error': _('User not found')},
            status=status.HTTP_404_NOT_FOUND
        ) 