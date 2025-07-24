"""
URL patterns for messaging.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MessageViewSet, InternalCommentViewSet

router = DefaultRouter()
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'comments', InternalCommentViewSet, basename='comment')

app_name = 'messaging'

urlpatterns = [
    path('', include(router.urls)),
] 