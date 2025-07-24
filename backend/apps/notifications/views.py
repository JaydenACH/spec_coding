"""
Notification management API endpoints.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import Notification, NotificationPreference
from .serializers import NotificationSerializer, NotificationPreferenceSerializer
from django.utils.translation import gettext_lazy as _

class NotificationViewSet(viewsets.ModelViewSet):
    """
    API endpoints for notification management.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return notifications for the current user."""
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')

    @extend_schema(
        summary="List notifications",
        description="Get list of notifications for the current user."
    )
    def list(self, request, *args, **kwargs):
        """List user notifications."""
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Mark notification as read",
        description="Mark a specific notification as read."
    )
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read."""
        notification = self.get_object()
        notification.mark_as_read()
        return Response({'message': _('Notification marked as read')}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Mark all notifications as read",
        description="Mark all notifications as read for the current user."
    )
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read."""
        count = Notification.objects.filter(
            recipient=request.user, 
            is_read=False
        ).update(is_read=True)
        return Response({'message': f'{count} notifications marked as read'}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Get unread count",
        description="Get count of unread notifications for the current user."
    )
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get unread notification count."""
        count = Notification.objects.filter(
            recipient=request.user, 
            is_read=False
        ).count()
        return Response({'unread_count': count}, status=status.HTTP_200_OK)


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    """
    API endpoints for notification preferences.
    """
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Return notification preferences for the current user."""
        return NotificationPreference.objects.filter(user=self.request.user)

    @extend_schema(
        summary="List notification preferences",
        description="Get notification preferences for the current user."
    )
    def list(self, request, *args, **kwargs):
        """List user notification preferences."""
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Update notification preferences",
        description="Update notification preferences for the current user."
    )
    def update(self, request, *args, **kwargs):
        """Update notification preferences."""
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Get or create default preferences",
        description="Get notification preferences or create defaults if they don't exist."
    )
    @action(detail=False, methods=['get'])
    def get_or_create_defaults(self, request):
        """Get or create default notification preferences."""
        preferences = NotificationPreference.create_default_preferences(request.user)
        serializer = self.get_serializer(preferences, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        """Create notification preference for current user."""
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """Update notification preference for current user."""
        serializer.save(user=self.request.user) 