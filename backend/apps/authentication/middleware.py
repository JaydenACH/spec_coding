"""
Custom middleware for authentication and security.
"""

from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.utils import timezone
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from .models import UserSession
import logging

logger = logging.getLogger(__name__)


class JWTAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware to handle JWT authentication for all requests.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_authenticator = JWTAuthentication()
        super().__init__(get_response)
    
    def process_request(self, request):
        """Process request for JWT authentication."""
        # Skip authentication for certain paths
        skip_paths = [
            '/api/auth/login/',
            '/api/auth/refresh/',
            '/api/health/',
            '/api/schema/',
            '/api/docs/',
            '/api/redoc/',
            '/admin/',
        ]
        
        if any(request.path.startswith(path) for path in skip_paths):
            return None
        
        # Try JWT authentication
        try:
            auth_result = self.jwt_authenticator.authenticate(request)
            if auth_result:
                request.user, request.auth = auth_result
                # Enforce first-time password change requirement
                if (
                    request.user.is_authenticated and
                    getattr(request.user, 'password_change_required', False)
                ):
                    # Allow only password change endpoint
                    if not (
                        request.path.startswith('/api/auth/profile/change-password/') or
                        request.path.startswith('/admin/')
                    ):
                        return JsonResponse(
                            {'error': 'Password change required', 'detail': 'You must change your password before continuing.'},
                            status=403
                        )
                # Update user session activity
                if hasattr(request, 'session') and request.session.session_key:
                    UserSession.objects.filter(
                        user=request.user,
                        session_key=request.session.session_key,
                        is_active=True
                    ).update(last_activity=timezone.now())
        
        except (InvalidToken, TokenError) as e:
            # Log authentication failure
            logger.warning(f"JWT authentication failed: {str(e)}")
            
            # For API endpoints, return JSON error
            if request.path.startswith('/api/'):
                return JsonResponse(
                    {'error': 'Authentication required', 'detail': str(e)},
                    status=401
                )
        
        return None


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add security headers to responses.
    """
    
    def process_response(self, request, response):
        """Add security headers to response."""
        # Only add headers for API responses
        if request.path.startswith('/api/'):
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-Frame-Options'] = 'DENY'
            response['X-XSS-Protection'] = '1; mode=block'
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            
            # Add CORS headers if not already set
            if not response.get('Access-Control-Allow-Origin'):
                response['Access-Control-Allow-Origin'] = '*'
            if not response.get('Access-Control-Allow-Methods'):
                response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
            if not response.get('Access-Control-Allow-Headers'):
                response['Access-Control-Allow-Headers'] = 'Authorization, Content-Type, Accept'
        
        return response


class SessionTimeoutMiddleware(MiddlewareMixin):
    """
    Middleware to handle session timeout.
    """
    
    def process_request(self, request):
        """Check session timeout."""
        if request.user.is_authenticated and hasattr(request, 'session'):
            session_key = request.session.session_key
            if session_key:
                try:
                    user_session = UserSession.objects.get(
                        user=request.user,
                        session_key=session_key,
                        is_active=True
                    )
                    
                    # Check if session has timed out (8 hours default)
                    timeout_hours = 8
                    timeout_delta = timezone.timedelta(hours=timeout_hours)
                    
                    if timezone.now() - user_session.last_activity > timeout_delta:
                        # Session has timed out
                        user_session.is_active = False
                        user_session.save()
                        
                        # Logout user and clear session
                        from django.contrib.auth import logout
                        logout(request)
                        
                        # For API requests, return JSON error
                        if request.path.startswith('/api/'):
                            return JsonResponse(
                                {'error': 'Session expired', 'detail': 'Please login again'},
                                status=401
                            )
                
                except UserSession.DoesNotExist:
                    # Session record not found, create one
                    ip_address = self.get_client_ip(request)
                    user_agent = request.META.get('HTTP_USER_AGENT', '')
                    
                    UserSession.objects.create(
                        user=request.user,
                        session_key=session_key,
                        ip_address=ip_address,
                        user_agent=user_agent,
                        is_active=True
                    )
        
        return None
    
    def get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class RateLimitMiddleware(MiddlewareMixin):
    """
    Simple rate limiting middleware for authentication endpoints.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit_cache = {}
        super().__init__(get_response)
    
    def process_request(self, request):
        """Apply rate limiting to sensitive endpoints."""
        # Rate limit authentication endpoints
        rate_limited_paths = [
            '/api/auth/login/',
            '/api/auth/refresh/',
        ]
        
        if any(request.path.startswith(path) for path in rate_limited_paths):
            ip_address = self.get_client_ip(request)
            current_time = timezone.now()
            
            # Clean old entries (older than 1 hour)
            cutoff_time = current_time - timezone.timedelta(hours=1)
            self.rate_limit_cache = {
                key: value for key, value in self.rate_limit_cache.items()
                if value['last_request'] > cutoff_time
            }
            
            # Check rate limit for this IP
            if ip_address in self.rate_limit_cache:
                cache_entry = self.rate_limit_cache[ip_address]
                
                # Allow 10 requests per hour
                if cache_entry['count'] >= 10:
                    return JsonResponse(
                        {'error': 'Rate limit exceeded', 'detail': 'Too many requests'},
                        status=429
                    )
                
                # Increment counter
                cache_entry['count'] += 1
                cache_entry['last_request'] = current_time
            else:
                # First request from this IP
                self.rate_limit_cache[ip_address] = {
                    'count': 1,
                    'last_request': current_time
                }
        
        return None
    
    def get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip 