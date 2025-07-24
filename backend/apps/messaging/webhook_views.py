"""
Respond.IO webhook endpoints for incoming messages and assignments.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from drf_spectacular.utils import extend_schema
from .models import Message
from apps.customers.models import Conversation, Customer
from .serializers import MessageSerializer
from django.utils import timezone
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class RespondIOMessageWebhook(APIView):
    permission_classes = [permissions.AllowAny]  # Token validation handled manually

    @extend_schema(
        summary="Respond.IO Message Webhook",
        description="Receive incoming messages from Respond.IO and create/update messages/conversations."
    )
    def post(self, request):
        # Basic token validation (stub for MVP)
        token = request.headers.get('X-Webhook-Token')
        expected_token = getattr(settings, 'RESPOND_IO_WEBHOOK_SECRET', None)
        if expected_token and token != expected_token:
            logger.warning('Invalid Respond.IO webhook token')
            return Response({'error': 'Invalid token'}, status=status.HTTP_403_FORBIDDEN)
        data = request.data
        # Parse payload (simplified for MVP)
        contact = data.get('contact', {})
        message = data.get('message', {})
        phone = contact.get('phone')
        content = message.get('message', {}).get('text')
        respond_io_message_id = message.get('messageId')
        # Find or create customer
        customer, _ = Customer.objects.get_or_create(phone_number=phone, defaults={'name': contact.get('firstName', '')})
        # Find or create conversation
        conversation, _ = Conversation.objects.get_or_create(customer=customer, defaults={'assigned_user': customer.assigned_user})
        # Create message
        msg = Message.objects.create(
            conversation=conversation,
            message_type='Text',
            content=content,
            sender_type='Customer',
            sender_customer=customer,
            respond_io_message_id=respond_io_message_id,
            sent_at=timezone.now(),
            status='Delivered'
        )
        logger.info(f'Received message from Respond.IO: {msg.id}')
        return Response({'message': 'Message received', 'id': msg.id}, status=status.HTTP_201_CREATED)

class RespondIOAssignmentWebhook(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Respond.IO Assignment Webhook",
        description="Receive assignment/unassignment events from Respond.IO and update assignments."
    )
    def post(self, request):
        # Basic token validation (stub for MVP)
        token = request.headers.get('X-Webhook-Token')
        expected_token = getattr(settings, 'RESPOND_IO_WEBHOOK_SECRET', None)
        if expected_token and token != expected_token:
            logger.warning('Invalid Respond.IO webhook token')
            return Response({'error': 'Invalid token'}, status=status.HTTP_403_FORBIDDEN)
        data = request.data
        contact = data.get('contact', {})
        assignee = contact.get('assignee')
        phone = contact.get('phone')
        # Find customer
        try:
            customer = Customer.objects.get(phone_number=phone)
        except Customer.DoesNotExist:
            return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
        # Update assignment
        if assignee and assignee.get('email'):
            from apps.authentication.models import User
            try:
                user = User.objects.get(email=assignee['email'])
                customer.assign_to_user(user, assigned_by=None)
            except User.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            customer.unassign(unassigned_by=None)
        logger.info(f'Assignment updated for customer {customer.id}')
        return Response({'message': 'Assignment updated'}, status=status.HTTP_200_OK) 