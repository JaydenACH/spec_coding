"""
Messaging and internal comments API endpoints.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import Message, InternalComment, Conversation
from .serializers import (
    MessageSerializer, MessageSendSerializer, MessageStatusSerializer,
    InternalCommentSerializer, InternalCommentCreateSerializer
)
from apps.authentication.permissions import IsSystemAdmin, IsManagerOrSystemAdmin, IsAssignedUserOrManager
from django.utils.translation import gettext_lazy as _

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

    @extend_schema(
        summary="Tag users in comment",
        description="Tag users in an internal comment using @username syntax."
    )
    @action(detail=True, methods=['post'])
    def tag(self, request, pk=None):
        comment = self.get_object()
        # Tagging logic handled in serializer/model signal
        return Response({'message': _('Users tagged successfully')}, status=status.HTTP_200_OK) 