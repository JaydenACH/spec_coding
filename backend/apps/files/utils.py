"""
File utility functions for validation, processing, and management.
"""

import os
import mimetypes
from PIL import Image
from django.core.files.base import ContentFile
from django.conf import settings
from .storage import secure_storage, FileValidator, FileAccessController
import logging

logger = logging.getLogger(__name__)

def process_uploaded_file(file_obj, user, description=''):
    """
    Process an uploaded file with validation, storage, and metadata creation.
    """
    try:
        # Validate file type
        valid_type, type_message = FileValidator.validate_file_type(file_obj)
        if not valid_type:
            raise ValueError(type_message)
        
        # Validate file size
        valid_size, size_message = FileValidator.validate_file_size(file_obj)
        if not valid_size:
            raise ValueError(size_message)
        
        # Save file securely
        file_info = secure_storage.save_file(
            file_obj, 
            file_obj.name, 
            file_obj.content_type
        )
        
        # Generate thumbnail for images (placeholder for MVP)
        thumbnail_path = None
        if file_obj.content_type and file_obj.content_type.startswith('image/'):
            thumbnail_path = generate_thumbnail(file_info['file_path'])
        
        # Perform virus scan (stub for MVP)
        scan_result, scan_message = FileValidator.scan_for_viruses(file_info['full_path'])
        
        # Create File model instance data
        file_data = {
            'original_filename': file_info['original_filename'],
            'file_path': file_info['file_path'],
            'content_type': file_info['content_type'],
            'file_size': file_info['file_size'],
            'file_hash': file_info['file_hash'],
            'uploaded_by': user,
            'description': description,
            'virus_scan_status': 'passed' if scan_result else 'failed',
            'virus_scan_result': scan_message,
            'thumbnail_path': thumbnail_path,
            'upload_source': 'web_upload'
        }
        
        return True, file_data
        
    except Exception as e:
        logger.error(f'Error processing uploaded file: {e}')
        return False, str(e)


def generate_thumbnail(file_path, max_size=(200, 200)):
    """
    Generate thumbnail for image files (placeholder for MVP).
    """
    try:
        full_path = secure_storage.path(file_path)
        
        # Check if file is an image
        mime_type, _ = mimetypes.guess_type(full_path)
        if not mime_type or not mime_type.startswith('image/'):
            return None
        
        # For MVP, just return a placeholder path
        # In production, you'd use PIL to generate actual thumbnails
        logger.info(f'Thumbnail generation (placeholder) for: {file_path}')
        
        # Return thumbnail path (would be actual generated thumbnail in production)
        base_name = os.path.splitext(file_path)[0]
        return f"{base_name}_thumb.jpg"
        
    except Exception as e:
        logger.error(f'Error generating thumbnail for {file_path}: {e}')
        return None


def get_file_type_from_content(file_obj):
    """
    Determine file type from content (stub for MVP).
    In production, use python-magic for content-based detection.
    """
    # For MVP, rely on content_type from upload
    content_type = getattr(file_obj, 'content_type', None)
    
    if content_type:
        if content_type.startswith('image/'):
            return 'Image'
        elif content_type == 'application/pdf':
            return 'Document'
        elif content_type.startswith('video/'):
            return 'Video'
        elif content_type.startswith('audio/'):
            return 'Audio'
    
    return 'Other'


def validate_file_access(user, file_obj, action='view'):
    """
    Validate if user can perform action on file.
    """
    if action == 'view' or action == 'download':
        return FileAccessController.can_user_download_file(user, file_obj)
    elif action == 'delete':
        return FileAccessController.can_user_delete_file(user, file_obj)
    
    return False


def clean_filename(filename):
    """
    Clean filename to prevent security issues.
    """
    # Remove path components
    filename = os.path.basename(filename)
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
    for char in dangerous_chars:
        filename = filename.replace(char, '_')
    
    # Limit length
    if len(filename) > 100:
        name, ext = os.path.splitext(filename)
        filename = name[:95] + ext
    
    return filename


def get_file_icon(file_type):
    """
    Get appropriate icon for file type.
    """
    icons = {
        'Image': 'image',
        'Document': 'file-text',
        'Video': 'video',
        'Audio': 'music',
        'Archive': 'archive',
        'Other': 'file'
    }
    
    return icons.get(file_type, 'file')


def format_file_size(size_bytes):
    """
    Format file size in human-readable format.
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    size_index = 0
    
    while size_bytes >= 1024 and size_index < len(size_names) - 1:
        size_bytes /= 1024.0
        size_index += 1
    
    return f"{size_bytes:.1f} {size_names[size_index]}"


def schedule_file_cleanup(file_obj):
    """
    Schedule file for cleanup (stub for MVP).
    In production, this would add to a cleanup queue.
    """
    logger.info(f'File scheduled for cleanup: {file_obj.file_path}')


def check_storage_quota(user, file_size):
    """
    Check if user has enough storage quota (stub for MVP).
    """
    # For MVP, assume unlimited storage
    return True, 'Storage available'


def create_file_backup(file_path):
    """
    Create backup of important files (stub for MVP).
    """
    logger.info(f'File backup (stub) for: {file_path}')
    return True 