"""
Authentication URL patterns.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    logout_view,
    UserProfileViewSet,
    UserManagementViewSet,
    LoginAttemptViewSet,
    auth_status,
    unlock_account
)

router = DefaultRouter()
router.register(r'users', UserManagementViewSet, basename='user')
router.register(r'login-attempts', LoginAttemptViewSet, basename='login-attempt')

urlpatterns = [
    # JWT Authentication endpoints
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', logout_view, name='logout'),
    
    # User profile endpoints
    path('profile/', UserProfileViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update'
    }), name='user_profile'),
    path('profile/change-password/', UserProfileViewSet.as_view({
        'post': 'change_password'
    }), name='change_password'),
    
    # Authentication status
    path('status/', auth_status, name='auth_status'),
    
    # Admin endpoints
    path('unlock-account/<uuid:user_id>/', unlock_account, name='unlock_account'),
    
    # Router URLs
    path('', include(router.urls)),
] 