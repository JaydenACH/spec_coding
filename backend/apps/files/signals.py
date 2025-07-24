"""
File signals for security scanning and sharing notifications.
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import File, FileShare


@receiver(post_save, sender=File)
def handle_file_upload(sender, instance, created, **kwargs):
    """Handle file upload and initiate security scanning."""
    if created:
        # Log file upload
        print(f"File uploaded: {instance.original_filename} by {instance.uploaded_by}")
        
        # TODO: Initiate virus scanning (implement with actual antivirus service)
        # For now, mark as pending scan
        if instance.virus_scan_status == File.VirusScanStatus.PENDING:
            # In a real implementation, this would trigger a background task
            # For MVP, we'll skip virus scanning and mark as clean
            instance.mark_virus_scan_complete(File.VirusScanStatus.SKIPPED, "Virus scanning disabled in MVP")


@receiver(post_save, sender=FileShare)
def handle_file_share(sender, instance, created, **kwargs):
    """Handle file sharing notifications."""
    if created:
        from apps.notifications.models import Notification
        
        # Notify specific user if shared with them
        if instance.shared_with_user:
            Notification.create_notification(
                recipient=instance.shared_with_user,
                notification_type=Notification.NotificationType.FILE_SHARE,
                title=f"File shared: {instance.file.original_filename}",
                message=f"{instance.shared_by.full_name} shared a file with you: {instance.file.original_filename}",
                content_object=instance,
                action_url=f"/files/{instance.file.id}/",
                priority=Notification.Priority.NORMAL,
                sender=instance.shared_by
            )
        
        # Notify role-based group
        elif instance.shared_with_role:
            from apps.authentication.models import User
            
            role_mapping = {
                'basic_user': User.Role.BASIC_USER,
                'manager': User.Role.MANAGER,
                'system_admin': User.Role.SYSTEM_ADMIN,
            }
            
            if instance.shared_with_role in role_mapping:
                users = User.objects.filter(
                    role=role_mapping[instance.shared_with_role]
                ).exclude(id=instance.shared_by.id)
                
                for user in users:
                    Notification.create_notification(
                        recipient=user,
                        notification_type=Notification.NotificationType.FILE_SHARE,
                        title=f"File shared with {instance.get_shared_with_role_display()}",
                        message=f"{instance.shared_by.full_name} shared: {instance.file.original_filename}",
                        content_object=instance,
                        action_url=f"/files/{instance.file.id}/",
                        priority=Notification.Priority.NORMAL,
                        sender=instance.shared_by
                    )


@receiver(post_delete, sender=File)
def handle_file_deletion(sender, instance, **kwargs):
    """Handle file deletion cleanup."""
    # Log file deletion
    print(f"File deleted: {instance.original_filename}")
    
    # TODO: Clean up physical file from storage
    # In a real implementation, this would remove the file from disk/S3 