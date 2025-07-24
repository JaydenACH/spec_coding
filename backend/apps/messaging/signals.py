"""
Messaging signals for notifications and conversation updates.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import Message, InternalComment, CommentMention


@receiver(post_save, sender=Message)
def handle_new_message(sender, instance, created, **kwargs):
    """Handle new message creation and notifications."""
    if created:
        # Update conversation timestamps and counters
        conversation = instance.conversation
        conversation.update_last_message_time()
        conversation.increment_message_count()
        
        # Update customer's last message date if message is from customer
        if instance.is_from_customer and conversation.customer:
            conversation.customer.last_message_date = instance.created_at
            conversation.customer.save(update_fields=['last_message_date'])
        
        # Create notification for assigned user if message is from customer
        if instance.is_from_customer and conversation.assigned_user:
            from apps.notifications.models import Notification
            
            Notification.create_notification(
                recipient=conversation.assigned_user,
                notification_type=Notification.NotificationType.MESSAGE,
                title=f"New message from {conversation.customer.display_name}",
                message=instance.content[:100] + ('...' if len(instance.content) > 100 else ''),
                content_object=instance,
                action_url=f"/conversations/{conversation.id}/",
                priority=Notification.Priority.NORMAL,
                sender=instance.sender_customer if instance.sender_customer else None
            )


@receiver(post_save, sender=InternalComment)
def handle_internal_comment(sender, instance, created, **kwargs):
    """Handle internal comment creation and notifications."""
    if created:
        # Update conversation comment count
        conversation = instance.conversation
        conversation.increment_comment_count()
        
        # Notify assigned user if comment is not from them
        if (instance.notify_assigned_user and 
            conversation.assigned_user and 
            conversation.assigned_user != instance.author):
            
            from apps.notifications.models import Notification
            
            priority = (Notification.Priority.HIGH if instance.is_high_priority 
                       else Notification.Priority.NORMAL)
            
            Notification.create_notification(
                recipient=conversation.assigned_user,
                notification_type=Notification.NotificationType.COMMENT,
                title=f"New comment on {conversation.customer.display_name}",
                message=f"{instance.author.full_name}: {instance.content[:100]}{'...' if len(instance.content) > 100 else ''}",
                content_object=instance,
                action_url=f"/conversations/{conversation.id}/#comment-{instance.id}",
                priority=priority,
                sender=instance.author
            )
        
        # Notify managers if requested
        if instance.notify_managers:
            from apps.authentication.models import User
            from apps.notifications.models import Notification
            
            managers = User.objects.filter(
                role__in=[User.Role.MANAGER, User.Role.SYSTEM_ADMIN]
            ).exclude(id=instance.author.id)
            
            for manager in managers:
                Notification.create_notification(
                    recipient=manager,
                    notification_type=Notification.NotificationType.COMMENT,
                    title=f"Team comment: {conversation.customer.display_name}",
                    message=f"{instance.author.full_name}: {instance.content[:100]}{'...' if len(instance.content) > 100 else ''}",
                    content_object=instance,
                    action_url=f"/conversations/{conversation.id}/#comment-{instance.id}",
                    priority=Notification.Priority.NORMAL,
                    sender=instance.author
                )


@receiver(post_save, sender=CommentMention)
def handle_comment_mention(sender, instance, created, **kwargs):
    """Handle user mentions in comments."""
    if created:
        from apps.notifications.models import Notification
        
        # Create mention notification
        Notification.create_notification(
            recipient=instance.mentioned_user,
            notification_type=Notification.NotificationType.MENTION,
            title=f"You were mentioned by {instance.mentioned_by.full_name}",
            message=f"In comment: {instance.comment.content[:100]}{'...' if len(instance.comment.content) > 100 else ''}",
            content_object=instance.comment,
            action_url=f"/conversations/{instance.comment.conversation.id}/#comment-{instance.comment.id}",
            priority=Notification.Priority.HIGH,
            sender=instance.mentioned_by
        )
        
        # Mark notification as sent
        instance.notification_sent = True
        instance.save(update_fields=['notification_sent']) 