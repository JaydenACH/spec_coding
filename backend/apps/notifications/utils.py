"""
Utility functions for real-time notification broadcasting.
"""

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification, NotificationPreference
import logging

logger = logging.getLogger(__name__)
channel_layer = get_channel_layer()


def send_notification_to_user(user, notification_data):
    """
    Send a real-time notification to a specific user.
    """
    if not channel_layer:
        logger.warning('Channel layer not configured')
        return
    
    user_group_name = f'user_{user.id}'
    
    try:
        async_to_sync(channel_layer.group_send)(
            user_group_name,
            {
                'type': 'notification',
                'notification': notification_data
            }
        )
        logger.info(f'Notification sent to user {user.email}')
    except Exception as e:
        logger.error(f'Error sending notification to user {user.email}: {e}')


def broadcast_assignment_notification(customer, assigned_user, assigned_by):
    """
    Broadcast customer assignment notification to the assigned user.
    """
    notification_data = {
        'id': None,  # Will be set when notification is created
        'type': 'assignment',
        'title': 'New Customer Assignment',
        'message': f'You have been assigned customer: {customer.display_name}',
        'customer_id': str(customer.id),
        'customer_name': customer.display_name,
        'assigned_by': assigned_by.full_name if assigned_by else 'System',
        'created_at': None,  # Will be set when notification is created
        'priority': 'normal'
    }
    
    # Create database notification
    notification = Notification.create_notification(
        recipient=assigned_user,
        notification_type='assignment',
        title=notification_data['title'],
        message=notification_data['message'],
        content_object=customer,
        sender=assigned_by
    )
    
    # Update notification data with DB info
    notification_data['id'] = str(notification.id)
    notification_data['created_at'] = notification.created_at.isoformat()
    
    # Send real-time notification
    send_notification_to_user(assigned_user, notification_data)


def broadcast_tag_notification(comment, tagged_user, tagged_by):
    """
    Broadcast user tag notification in internal comment.
    """
    notification_data = {
        'id': None,
        'type': 'mention',
        'title': 'You were mentioned',
        'message': f'{tagged_by.full_name} mentioned you in a comment',
        'comment_id': str(comment.id),
        'conversation_id': str(comment.conversation.id),
        'customer_name': comment.conversation.customer.display_name,
        'tagged_by': tagged_by.full_name,
        'created_at': None,
        'priority': 'normal'
    }
    
    # Create database notification
    notification = Notification.create_notification(
        recipient=tagged_user,
        notification_type='mention',
        title=notification_data['title'],
        message=notification_data['message'],
        content_object=comment,
        sender=tagged_by
    )
    
    # Update notification data with DB info
    notification_data['id'] = str(notification.id)
    notification_data['created_at'] = notification.created_at.isoformat()
    
    # Send real-time notification
    send_notification_to_user(tagged_user, notification_data)


def broadcast_message_notification(message, recipient):
    """
    Broadcast new message notification to assigned user.
    """
    notification_data = {
        'id': None,
        'type': 'message',
        'title': 'New Message',
        'message': f'New message from {message.conversation.customer.display_name}',
        'message_id': str(message.id),
        'conversation_id': str(message.conversation.id),
        'customer_name': message.conversation.customer.display_name,
        'sender_name': message.sender_name,
        'content_preview': message.content[:100] if message.content else 'File attachment',
        'created_at': None,
        'priority': 'normal'
    }
    
    # Create database notification
    notification = Notification.create_notification(
        recipient=recipient,
        notification_type='message',
        title=notification_data['title'],
        message=notification_data['message'],
        content_object=message,
        sender=None
    )
    
    # Update notification data with DB info
    notification_data['id'] = str(notification.id)
    notification_data['created_at'] = notification.created_at.isoformat()
    
    # Send real-time notification
    send_notification_to_user(recipient, notification_data)


def broadcast_unassigned_customer_notification(customer, managers):
    """
    Broadcast unassigned customer notification to all managers.
    """
    notification_data = {
        'id': None,
        'type': 'unassigned_customer',
        'title': 'Unassigned Customer',
        'message': f'Customer {customer.display_name} needs assignment',
        'customer_id': str(customer.id),
        'customer_name': customer.display_name,
        'phone_number': customer.formatted_phone_number,
        'created_at': None,
        'priority': 'high'
    }
    
    for manager in managers:
        # Create database notification for each manager
        notification = Notification.create_notification(
            recipient=manager,
            notification_type='unassigned_customer',
            title=notification_data['title'],
            message=notification_data['message'],
            content_object=customer,
            priority='high'
        )
        
        # Update notification data with DB info
        manager_notification_data = notification_data.copy()
        manager_notification_data['id'] = str(notification.id)
        manager_notification_data['created_at'] = notification.created_at.isoformat()
        
        # Send real-time notification
        send_notification_to_user(manager, manager_notification_data)


def check_notification_preferences(user, notification_type):
    """
    Check if user should receive notifications of this type.
    """
    try:
        preference = NotificationPreference.get_user_preference(user, notification_type)
        if preference:
            return preference.should_send_notification()
        return True  # Default to sending notifications
    except Exception as e:
        logger.error(f'Error checking notification preferences: {e}')
        return True


def send_notification_with_preferences(user, notification_type, notification_data):
    """
    Send notification only if user preferences allow it.
    """
    if check_notification_preferences(user, notification_type):
        send_notification_to_user(user, notification_data)
    else:
        logger.info(f'Notification blocked by user preferences: {user.email}, type: {notification_type}') 