"""
URL patterns for file management.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FileViewSet

router = DefaultRouter()
router.register(r'', FileViewSet, basename='file')

app_name = 'files'

urlpatterns = [
    path('', include(router.urls)),
] 