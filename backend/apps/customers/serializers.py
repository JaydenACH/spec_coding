"""
Serializers for customer management and assignment.
"""

from rest_framework import serializers
from .models import Customer
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field
User = get_user_model()

class CustomerSerializer(serializers.ModelSerializer):
    assigned_user_email = serializers.EmailField(source='assigned_user.email', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    @extend_schema_field(serializers.BooleanField())
    def is_assigned(self) -> bool:
        return self.instance.is_assigned

    @extend_schema_field(serializers.CharField())
    def formatted_phone_number(self) -> str:
        return self.instance.formatted_phone_number

    class Meta:
        model = Customer
        fields = [
            'id', 'phone_number', 'name', 'status', 'status_display', 'assigned_user',
            'assigned_user_email', 'respond_io_contact_id', 'email', 'language',
            'country_code', 'profile_picture_url', 'first_contact_date', 'last_message_date',
            'assignment_history', 'display_name', 'is_assigned', 'formatted_phone_number'
        ]
        read_only_fields = ['id', 'assignment_history', 'display_name', 'is_assigned', 'formatted_phone_number']

class CustomerAssignmentSerializer(serializers.Serializer):
    assigned_user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

class AssignmentHistorySerializer(serializers.Serializer):
    assigned_to = serializers.CharField()
    assigned_by = serializers.CharField()
    assigned_at = serializers.DateTimeField()
    unassigned_by = serializers.CharField(required=False)
    unassigned_at = serializers.DateTimeField(required=False) 