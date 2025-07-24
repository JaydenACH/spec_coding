"""
Serializers for notification models.
"""

from rest_framework import serializers
from .models import Notification, NotificationPreference
from drf_spectacular.utils import extend_schema_field

class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for Notification model.
    """
    content_type_name = serializers.CharField(source='content_type.model', read_only=True)
    sender_name = serializers.CharField(source='sender.full_name', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    @extend_schema_field(serializers.BooleanField())
    def is_expired(self) -> bool:
        return self.instance.is_expired

    @extend_schema_field(serializers.BooleanField())
    def is_high_priority(self) -> bool:
        return self.instance.is_high_priority

    @extend_schema_field(serializers.BooleanField())
    def is_scheduled(self) -> bool:
        return self.instance.is_scheduled

    class Meta:
        model = Notification
        fields = [
            'id', 'notification_type', 'title', 'message', 'priority', 'priority_display',
            'status', 'status_display', 'is_read', 'read_at', 'content_type_name',
            'object_id', 'action_url', 'action_data', 'sender_name', 'in_app_delivered',
            'email_delivered', 'push_delivered', 'expires_at', 'group_key',
            'scheduled_for', 'sent_at', 'created_at', 'is_expired', 'is_high_priority',
            'is_scheduled'
        ]
        read_only_fields = [
            'id', 'created_at', 'sent_at', 'read_at', 'content_type_name', 
            'sender_name', 'priority_display', 'status_display', 'is_expired',
            'is_high_priority', 'is_scheduled'
        ]


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """
    Serializer for NotificationPreference model.
    """
    delivery_method_display = serializers.CharField(source='get_delivery_method_display', read_only=True)
    minimum_priority_display = serializers.CharField(source='get_minimum_priority_display', read_only=True)
    digest_frequency_display = serializers.CharField(source='get_digest_frequency_display', read_only=True)

    @extend_schema_field(serializers.BooleanField())
    def is_in_quiet_hours(self) -> bool:
        return self.instance.is_in_quiet_hours

    @extend_schema_field(serializers.BooleanField())
    def is_weekend_and_disabled(self) -> bool:
        return self.instance.is_weekend_and_disabled

    class Meta:
        model = NotificationPreference
        fields = [
            'id', 'notification_type', 'delivery_method', 'delivery_method_display',
            'is_enabled', 'minimum_priority', 'minimum_priority_display',
            'quiet_hours_start', 'quiet_hours_end', 'weekend_enabled',
            'digest_frequency', 'digest_frequency_display', 'max_per_day',
            'is_in_quiet_hours', 'is_weekend_and_disabled'
        ]
        read_only_fields = [
            'id', 'delivery_method_display', 'minimum_priority_display',
            'digest_frequency_display', 'is_in_quiet_hours', 'is_weekend_and_disabled'
        ]

    def validate_quiet_hours_start(self, value):
        """Validate quiet hours start time."""
        if value and (value < 0 or value > 23):
            raise serializers.ValidationError('Quiet hours start must be between 0 and 23.')
        return value

    def validate_quiet_hours_end(self, value):
        """Validate quiet hours end time."""
        if value and (value < 0 or value > 23):
            raise serializers.ValidationError('Quiet hours end must be between 0 and 23.')
        return value

    def validate_max_per_day(self, value):
        """Validate max notifications per day."""
        if value and value < 1:
            raise serializers.ValidationError('Max per day must be at least 1.')
        return value 