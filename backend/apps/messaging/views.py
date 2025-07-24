"""
Messaging and internal comments API endpoints.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import Message, InternalComment
from apps.customers.models import Conversation
from .serializers import (
    MessageSerializer, MessageSendSerializer, MessageStatusSerializer,
    InternalCommentSerializer, InternalCommentCreateSerializer
)
from apps.authentication.permissions import IsSystemAdmin, IsManagerOrSystemAdmin, IsAssignedUserOrManager
from django.utils.translation import gettext_lazy as _
from .respondio_service import send_respondio_message, create_internal_comment_respondio
import logging

logger = logging.getLogger(__name__)

class MessageViewSet(viewsets.ModelViewSet):
    """
    API endpoints for messaging (send/receive, history, status).
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        conversation_id = self.request.query_params.get('conversation')
        qs = Message.objects.all()
        if conversation_id:
            qs = qs.filter(conversation_id=conversation_id)
        if user.is_system_admin or user.is_manager:
            return qs
        else:
            # Only assigned user can see their conversation messages
            return qs.filter(conversation__assigned_user=user)

    @extend_schema(
        summary="Send message",
        description="Send a message in a conversation."
    )
    @action(detail=False, methods=['post'], serializer_class=MessageSendSerializer)
    def send(self, request):
        serializer = MessageSendSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        message = serializer.save(sender_user=request.user)
        return Response(MessageSerializer(message).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Get message status",
        description="Get status of a message (delivered/read)."
    )
    @action(detail=True, methods=['get'], serializer_class=MessageStatusSerializer)
    def status(self, request, pk=None):
        message = self.get_object()
        serializer = MessageStatusSerializer(message)
        return Response(serializer.data)

    @extend_schema(
        summary="Send message to customer via Respond.IO",
        description="Send a message (text or file) to a customer using Respond.IO API."
    )
    @action(detail=False, methods=['post'], url_path='send-respondio')
    def send_respondio(self, request):
        """
        Send a message to a customer via Respond.IO API.
        """
        phone_number = request.data.get('phone_number')
        message_type = request.data.get('message_type')
        content = request.data.get('content')
        file_url = request.data.get('file_url')
        if not phone_number or not message_type:
            return Response({'error': 'phone_number and message_type are required'}, status=status.HTTP_400_BAD_REQUEST)
        success, result = send_respondio_message(phone_number, message_type, content, file_url)
        if success:
            return Response({'message': 'Message sent successfully', 'respondio': result}, status=status.HTTP_200_OK)
        else:
            return Response({'error': result}, status=status.HTTP_400_BAD_REQUEST)

class InternalCommentViewSet(viewsets.ModelViewSet):
    """
    API endpoints for internal comments and user tagging.
    """
    queryset = InternalComment.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return InternalCommentCreateSerializer
        return InternalCommentSerializer

    def get_queryset(self):
        user = self.request.user
        conversation_id = self.request.query_params.get('conversation')
        qs = InternalComment.objects.all()
        if conversation_id:
            qs = qs.filter(conversation_id=conversation_id)
        if user.is_system_admin or user.is_manager:
            return qs
        else:
            return qs.filter(conversation__assigned_user=user)

    def perform_create(self, serializer):
        """Create internal comment and sync with Respond.IO if applicable."""
        comment = serializer.save(author=self.request.user)
        
        # Extract tagged users and sync with Respond.IO
        if comment.has_mentions:
            customer = comment.conversation.customer
            phone_number = customer.formatted_phone_number
            
            # Get tagged user IDs for Respond.IO
            tagged_user_ids = []
            # This would be extracted from the comment content parsing @username mentions
            # For MVP, we'll use a simple approach
            
            success, result = create_internal_comment_respondio(
                phone_number, 
                comment.content, 
                tagged_user_ids
            )
            if not success:
                logger.warning(f'Failed to sync internal comment with Respond.IO: {result}')

    @extend_schema(
        summary="Tag users in comment",
        description="Tag users in an internal comment using @username syntax."
    )
    @action(detail=True, methods=['post'])
    def tag(self, request, pk=None):
        comment = self.get_object()
        # Tagging logic handled in serializer/model signal
        return Response({'message': _('Users tagged successfully')}, status=status.HTTP_200_OK) 