"""
Notification signals for processing and delivery.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification, NotificationPreference


@receiver(post_save, sender=Notification)
def process_notification(sender, instance, created, **kwargs):
    """Process notification based on user preferences."""
    if created:
        # Check user preferences for delivery methods
        delivery_methods = [
            NotificationPreference.DeliveryMethod.IN_APP,
            NotificationPreference.DeliveryMethod.EMAIL,
            NotificationPreference.DeliveryMethod.PUSH,
        ]
        
        for method in delivery_methods:
            preference = NotificationPreference.get_user_preference(
                instance.recipient,
                instance.notification_type,
                method
            )
            
            if preference.should_send_notification(instance):
                # Mark as delivered for in-app notifications immediately
                if method == NotificationPreference.DeliveryMethod.IN_APP:
                    instance.mark_as_delivered('in_app')
                
                # TODO: Implement email and push notification delivery
                # For MVP, we'll focus on in-app notifications
                elif method == NotificationPreference.DeliveryMethod.EMAIL:
                    # In a real implementation, this would queue an email
                    print(f"Email notification queued for {instance.recipient.email}: {instance.title}")
                
                elif method == NotificationPreference.DeliveryMethod.PUSH:
                    # In a real implementation, this would send a push notification
                    print(f"Push notification queued for {instance.recipient.full_name}: {instance.title}") 