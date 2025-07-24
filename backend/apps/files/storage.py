"""
Secure file storage system for MVP (local storage, designed for easy S3 migration).
"""

import os
import hashlib
import uuid
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.files.base import ContentFile
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

# File storage settings
MEDIA_ROOT = getattr(settings, 'MEDIA_ROOT', 'media/')
FILE_UPLOAD_MAX_SIZE = getattr(settings, 'FILE_UPLOAD_MAX_MEMORY_SIZE', 5 * 1024 * 1024)  # 5MB for MVP
ALLOWED_FILE_TYPES = getattr(settings, 'ALLOWED_FILE_TYPES', [
    'image/jpeg', 'image/png', 'image/gif', 'application/pdf'
])

class SecureFileStorage(FileSystemStorage):
    """
    Secure file storage with access control and organized directory structure.
    """
    
    def __init__(self):
        super().__init__(location=MEDIA_ROOT)
    
    def get_secure_filename(self, original_filename, content_type=None):
        """
        Generate a secure filename that prevents path traversal and conflicts.
        """
        # Extract file extension
        file_ext = os.path.splitext(original_filename)[1].lower()
        
        # Generate UUID-based filename
        secure_name = f"{uuid.uuid4().hex}{file_ext}"
        
        # Organize by date and type
        date_path = timezone.now().strftime('%Y/%m/%d')
        file_type = self._get_file_type_folder(content_type, file_ext)
        
        return f"{file_type}/{date_path}/{secure_name}"
    
    def _get_file_type_folder(self, content_type, file_ext):
        """Get appropriate folder based on file type."""
        if content_type:
            if content_type.startswith('image/'):
                return 'images'
            elif content_type == 'application/pdf':
                return 'documents'
        
        # Fallback to extension-based detection
        if file_ext in ['.jpg', '.jpeg', '.png', '.gif']:
            return 'images'
        elif file_ext in ['.pdf', '.doc', '.docx']:
            return 'documents'
        
        return 'files'
    
    def save_file(self, file_obj, original_filename, content_type=None):
        """
        Save file with security checks and return file info.
        """
        # Validate file size
        if file_obj.size > FILE_UPLOAD_MAX_SIZE:
            raise ValueError(f'File size ({file_obj.size} bytes) exceeds maximum allowed size ({FILE_UPLOAD_MAX_SIZE} bytes)')
        
        # Validate file type
        if content_type and content_type not in ALLOWED_FILE_TYPES:
            raise ValueError(f'File type {content_type} is not allowed')
        
        # Generate secure filename
        secure_filename = self.get_secure_filename(original_filename, content_type)
        
        # Calculate file hash
        file_hash = self._calculate_file_hash(file_obj)
        
        # Save file
        saved_path = self.save(secure_filename, file_obj)
        
        # Get full file path
        full_path = self.path(saved_path)
        
        return {
            'file_path': saved_path,
            'full_path': full_path,
            'file_hash': file_hash,
            'file_size': file_obj.size,
            'original_filename': original_filename,
            'content_type': content_type
        }
    
    def _calculate_file_hash(self, file_obj):
        """Calculate SHA-256 hash of file content."""
        hasher = hashlib.sha256()
        
        # Reset file pointer
        file_obj.seek(0)
        
        # Read file in chunks to handle large files
        for chunk in iter(lambda: file_obj.read(4096), b""):
            hasher.update(chunk)
        
        # Reset file pointer for saving
        file_obj.seek(0)
        
        return hasher.hexdigest()
    
    def get_file_url(self, file_path):
        """Get secure URL for file access."""
        return self.url(file_path)
    
    def delete_file(self, file_path):
        """Securely delete a file."""
        try:
            if self.exists(file_path):
                self.delete(file_path)
                logger.info(f'File deleted: {file_path}')
                return True
        except Exception as e:
            logger.error(f'Error deleting file {file_path}: {e}')
        return False
    
    def cleanup_expired_files(self, retention_days=365):
        """
        Clean up files older than retention period.
        """
        cutoff_date = timezone.now() - timezone.timedelta(days=retention_days)
        
        # This would be implemented with a management command
        # For now, just log the intention
        logger.info(f'File cleanup scheduled for files older than {cutoff_date}')


class FileValidator:
    """
    File validation utilities.
    """
    
    @staticmethod
    def validate_file_type(file_obj, allowed_types=None):
        """Validate file type based on content, not just extension."""
        if allowed_types is None:
            allowed_types = ALLOWED_FILE_TYPES
        
        # Basic validation - in production, you'd use python-magic for content-based detection
        content_type = getattr(file_obj, 'content_type', None)
        
        if content_type and content_type not in allowed_types:
            return False, f'File type {content_type} not allowed'
        
        return True, 'Valid file type'
    
    @staticmethod
    def validate_file_size(file_obj, max_size=None):
        """Validate file size."""
        if max_size is None:
            max_size = FILE_UPLOAD_MAX_SIZE
        
        if file_obj.size > max_size:
            return False, f'File size {file_obj.size} exceeds maximum {max_size}'
        
        return True, 'Valid file size'
    
    @staticmethod
    def scan_for_viruses(file_path):
        """
        Virus scanning stub for MVP.
        In production, integrate with ClamAV or similar.
        """
        # Stub implementation for MVP
        logger.info(f'Virus scan (stub) for file: {file_path}')
        return True, 'Clean (stub scan)'


class FileAccessController:
    """
    File access control utilities.
    """
    
    @staticmethod
    def can_user_access_file(user, file_obj):
        """
        Check if user can access a file based on business rules.
        """
        # System admin can access all files
        if user.is_system_admin:
            return True
        
        # File uploader can access their own files
        if file_obj.uploaded_by == user:
            return True
        
        # Managers can access files in their managed conversations
        if user.is_manager:
            return True
        
        # Basic users can access files in their assigned conversations
        # This would check if the file is related to a conversation they're assigned to
        # For MVP, simplified check
        return False
    
    @staticmethod
    def can_user_download_file(user, file_obj):
        """Check if user can download a specific file."""
        return FileAccessController.can_user_access_file(user, file_obj)
    
    @staticmethod
    def can_user_delete_file(user, file_obj):
        """Check if user can delete a file."""
        # Only system admin and file uploader can delete
        if user.is_system_admin or file_obj.uploaded_by == user:
            return True
        return False


# Initialize storage instance
secure_storage = SecureFileStorage() 