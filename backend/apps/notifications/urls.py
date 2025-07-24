"""
URL patterns for notification management.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, NotificationPreferenceViewSet

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'preferences', NotificationPreferenceViewSet, basename='notification-preference')

app_name = 'notifications'

urlpatterns = [
    path('api/', include(router.urls)),
] 