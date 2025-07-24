"""
Serializers for messaging and internal comments.
"""

from rest_framework import serializers
from .models import Message, InternalComment
from apps.customers.models import Conversation
from drf_spectacular.utils import extend_schema_field

class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    @extend_schema_field(serializers.BooleanField())
    def has_media(self) -> bool:
        return self.instance.has_media

    @extend_schema_field(serializers.BooleanField())
    def is_from_customer(self) -> bool:
        return self.instance.is_from_customer

    @extend_schema_field(serializers.BooleanField())
    def is_from_user(self) -> bool:
        return self.instance.is_from_user

    @extend_schema_field(serializers.BooleanField())
    def is_location_message(self) -> bool:
        return self.instance.is_location_message

    @extend_schema_field(serializers.BooleanField())
    def is_contact_message(self) -> bool:
        return self.instance.is_contact_message

    class Meta:
        model = Message
        fields = [
            'id', 'conversation', 'message_type', 'content', 'sender_type', 'sender_user',
            'sender_customer', 'status', 'status_display', 'read_by_user', 'read_at',
            'sent_at', 'edited_at', 'edit_count', 'media_url', 'reply_to', 'forwarded_from',
            'latitude', 'longitude', 'location_name', 'contact_name', 'contact_phone',
            'sender_name', 'has_media', 'is_from_customer', 'is_from_user', 'is_location_message',
            'is_contact_message', 'respond_io_message_id'
        ]
        read_only_fields = ['id', 'sent_at', 'edited_at', 'edit_count', 'sender_name', 'has_media', 'is_from_customer', 'is_from_user', 'is_location_message', 'is_contact_message']

class MessageSendSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['conversation', 'message_type', 'content', 'media_url', 'reply_to']

    def validate(self, attrs):
        # Add custom validation for message sending
        if not attrs.get('content') and not attrs.get('media_url'):
            raise serializers.ValidationError('Message content or media is required.')
        return attrs

    def create(self, validated_data):
        sender_user = self.context['request'].user
        return Message.objects.create(sender_user=sender_user, **validated_data)

class MessageStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'status', 'read_by_user', 'read_at']

class InternalCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.full_name', read_only=True)

    @extend_schema_field(serializers.BooleanField())
    def is_reply(self) -> bool:
        return self.instance.is_reply

    @extend_schema_field(serializers.BooleanField())
    def has_mentions(self) -> bool:
        return self.instance.has_mentions

    @extend_schema_field(serializers.BooleanField())
    def is_high_priority(self) -> bool:
        return self.instance.is_high_priority

    class Meta:
        model = InternalComment
        fields = [
            'id', 'conversation', 'author', 'author_name', 'content', 'priority',
            'reply_to', 'is_private', 'notify_assigned_user', 'notify_managers',
            'edited_at', 'is_reply', 'has_mentions', 'is_high_priority'
        ]
        read_only_fields = ['id', 'author_name', 'is_reply', 'has_mentions', 'is_high_priority']

class InternalCommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = InternalComment
        fields = ['conversation', 'content', 'priority', 'reply_to', 'is_private', 'notify_assigned_user', 'notify_managers'] 