"""
Customer signals for conversation and assignment management.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Customer, Conversation
from django.utils import timezone


@receiver(post_save, sender=Customer)
def handle_customer_assignment(sender, instance, created, **kwargs):
    """Handle customer assignment changes and create notifications."""
    if not created and instance.assigned_user:
        # Import here to avoid circular imports
        from apps.notifications.models import Notification
        
        # Create assignment notification
        Notification.create_notification(
            recipient=instance.assigned_user,
            notification_type=Notification.NotificationType.ASSIGNMENT,
            title=f"Customer Assigned: {instance.display_name}",
            message=f"You have been assigned to customer {instance.display_name} ({instance.formatted_phone_number})",
            content_object=instance,
            action_url=f"/customers/{instance.id}/",
            priority=Notification.Priority.NORMAL
        )


@receiver(post_save, sender=Conversation)
def handle_conversation_creation(sender, instance, created, **kwargs):
    """Handle new conversation creation."""
    if created:
        # Update customer's last message date
        if instance.customer:
            instance.customer.last_message_date = instance.created_at
            instance.customer.save(update_fields=['last_message_date'])
        
        print(f"Created conversation: {instance.id} for customer {instance.customer.display_name}")


@receiver(pre_save, sender=Conversation)
def update_conversation_timestamps(sender, instance, **kwargs):
    """Update conversation timestamps when status changes."""
    if instance.pk:  # Only for existing conversations
        try:
            old_instance = Conversation.objects.get(pk=instance.pk)
            
            # If conversation is being closed
            if (old_instance.status == Conversation.Status.ACTIVE and 
                instance.status == Conversation.Status.CLOSED):
                instance.closed_at = timezone.now()
            
            # If conversation is being reopened
            elif (old_instance.status == Conversation.Status.CLOSED and 
                  instance.status == Conversation.Status.ACTIVE):
                instance.closed_at = None
                instance.closed_by = None
                
        except Conversation.DoesNotExist:
            pass 