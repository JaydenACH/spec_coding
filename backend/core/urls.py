"""
URL configuration for Respond IO Alternate Interface.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

# API URL patterns
api_patterns = [
    # API Documentation
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # Health check
    path('health/', include('health_check.urls')),
    
    # Authentication endpoints
    path('auth/', include('apps.authentication.urls')),
    
    # Customer management endpoints
    path('customers/', include('apps.customers.urls')),
    
    # Messaging endpoints
    path('messaging/', include('apps.messaging.urls')),
    
    # File management endpoints
    path('files/', include('apps.files.urls')),
    
    # Notification endpoints
    path('notifications/', include('apps.notifications.urls')),
    
    # Webhook endpoints
    path('webhooks/', include('apps.messaging.webhook_urls')),
]

# Main URL patterns
urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/', include(api_patterns)),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin site configuration
admin.site.site_header = 'Respond IO Alternate Interface'
admin.site.site_title = 'Respond IO Admin'
admin.site.index_title = 'Administration' 