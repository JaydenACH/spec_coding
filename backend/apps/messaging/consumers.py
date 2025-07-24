"""
WebSocket consumers for real-time messaging.
"""

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import Message, Conversation, TypingIndicator
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time chat messaging.
    """

    async def connect(self):
        """Accept WebSocket connection and join conversation room."""
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'
        self.user = self.scope['user']

        # Check if user is authenticated
        if not self.user.is_authenticated:
            await self.close()
            return

        # Check if user has access to this conversation
        has_access = await self.check_conversation_access()
        if not has_access:
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f'User {self.user.email} connected to conversation {self.conversation_id}')

    async def disconnect(self, close_code):
        """Leave room group and clean up typing indicators."""
        # Stop typing indicator
        await self.stop_typing()
        
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        logger.info(f'User {self.user.email} disconnected from conversation {self.conversation_id}')

    async def receive(self, text_data):
        """Receive message from WebSocket."""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            if message_type == 'chat_message':
                await self.handle_chat_message(text_data_json)
            elif message_type == 'typing_start':
                await self.handle_typing_start()
            elif message_type == 'typing_stop':
                await self.handle_typing_stop()
            elif message_type == 'message_read':
                await self.handle_message_read(text_data_json)
                
        except json.JSONDecodeError:
            logger.error(f'Invalid JSON received: {text_data}')
        except Exception as e:
            logger.error(f'Error handling WebSocket message: {e}')

    async def handle_chat_message(self, data):
        """Handle incoming chat message."""
        content = data.get('content')
        reply_to_id = data.get('reply_to')
        
        if not content:
            return
        
        # Save message to database
        message = await self.save_message(content, reply_to_id)
        
        if message:
            # Broadcast message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': {
                        'id': str(message.id),
                        'content': message.content,
                        'sender_name': message.sender_name,
                        'sender_user_id': str(message.sender_user.id) if message.sender_user else None,
                        'sent_at': message.sent_at.isoformat(),
                        'reply_to': str(message.reply_to.id) if message.reply_to else None,
                        'message_type': message.message_type
                    }
                }
            )

    async def handle_typing_start(self):
        """Handle typing start indicator."""
        await self.set_typing(True)
        
        # Broadcast typing indicator to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'user_id': str(self.user.id),
                'user_name': self.user.full_name,
                'is_typing': True
            }
        )

    async def handle_typing_stop(self):
        """Handle typing stop indicator."""
        await self.set_typing(False)
        
        # Broadcast typing stop to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'typing_indicator',
                'user_id': str(self.user.id),
                'user_name': self.user.full_name,
                'is_typing': False
            }
        )

    async def handle_message_read(self, data):
        """Handle message read status."""
        message_id = data.get('message_id')
        if message_id:
            await self.mark_message_read(message_id)
            
            # Broadcast read status to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'message_read',
                    'message_id': message_id,
                    'read_by': str(self.user.id),
                    'read_at': timezone.now().isoformat()
                }
            )

    # Event handlers for group messages

    async def chat_message(self, event):
        """Send chat message to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message']
        }))

    async def typing_indicator(self, event):
        """Send typing indicator to WebSocket."""
        # Don't send typing indicator to the user who is typing
        if event['user_id'] != str(self.user.id):
            await self.send(text_data=json.dumps({
                'type': 'typing_indicator',
                'user_id': event['user_id'],
                'user_name': event['user_name'],
                'is_typing': event['is_typing']
            }))

    async def message_read(self, event):
        """Send message read status to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'message_read',
            'message_id': event['message_id'],
            'read_by': event['read_by'],
            'read_at': event['read_at']
        }))

    async def notification(self, event):
        """Send notification to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': event['notification']
        }))

    # Database operations

    @database_sync_to_async
    def check_conversation_access(self):
        """Check if user has access to the conversation."""
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            if self.user.is_system_admin or self.user.is_manager:
                return True
            return conversation.assigned_user == self.user
        except Conversation.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, content, reply_to_id=None):
        """Save message to database."""
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            reply_to = None
            if reply_to_id:
                try:
                    reply_to = Message.objects.get(id=reply_to_id)
                except Message.DoesNotExist:
                    pass
            
            message = Message.objects.create(
                conversation=conversation,
                content=content,
                sender_user=self.user,
                sender_type='User',
                message_type='Text',
                reply_to=reply_to,
                sent_at=timezone.now(),
                status='Sent'
            )
            return message
        except Exception as e:
            logger.error(f'Error saving message: {e}')
            return None

    @database_sync_to_async
    def set_typing(self, is_typing):
        """Set typing indicator for user."""
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            if is_typing:
                TypingIndicator.set_typing(conversation, self.user)
            else:
                TypingIndicator.stop_typing(conversation, self.user)
        except Exception as e:
            logger.error(f'Error setting typing indicator: {e}')

    @database_sync_to_async
    def stop_typing(self):
        """Stop typing indicator for user."""
        try:
            conversation = Conversation.objects.get(id=self.conversation_id)
            TypingIndicator.stop_typing(conversation, self.user)
        except Exception as e:
            logger.error(f'Error stopping typing indicator: {e}')

    @database_sync_to_async
    def mark_message_read(self, message_id):
        """Mark message as read."""
        try:
            message = Message.objects.get(id=message_id)
            message.mark_as_read(self.user)
        except Message.DoesNotExist:
            pass
        except Exception as e:
            logger.error(f'Error marking message as read: {e}')


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time notifications.
    """

    async def connect(self):
        """Accept WebSocket connection for notifications."""
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        self.user_group_name = f'user_{self.user.id}'
        
        # Join user notification group
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        
        await self.accept()
        logger.info(f'User {self.user.email} connected to notifications')

    async def disconnect(self, close_code):
        """Leave notification group."""
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )
        logger.info(f'User {self.user.email} disconnected from notifications')

    async def receive(self, text_data):
        """Receive notification acknowledgment from WebSocket."""
        try:
            text_data_json = json.loads(text_data)
            if text_data_json.get('type') == 'notification_ack':
                notification_id = text_data_json.get('notification_id')
                await self.mark_notification_read(notification_id)
        except Exception as e:
            logger.error(f'Error handling notification acknowledgment: {e}')

    async def notification(self, event):
        """Send notification to WebSocket."""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': event['notification']
        }))

    @database_sync_to_async
    def mark_notification_read(self, notification_id):
        """Mark notification as read."""
        try:
            from apps.notifications.models import Notification
            notification = Notification.objects.get(id=notification_id, recipient=self.user)
            notification.mark_as_read()
        except Exception as e:
            logger.error(f'Error marking notification as read: {e}') 