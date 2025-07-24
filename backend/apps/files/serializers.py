"""
Serializers for file upload/download.
"""

from rest_framework import serializers
from .models import File

class FileSerializer(serializers.ModelSerializer):
    uploaded_by_email = serializers.EmailField(source='uploaded_by.email', read_only=True)
    file_size_human = serializers.CharField(read_only=True)
    class Meta:
        model = File
        fields = [
            'id', 'original_filename', 'file_path', 'content_type', 'file_type', 'file_size',
            'file_size_human', 'file_hash', 'virus_scan_status', 'virus_scan_result',
            'virus_scanned_at', 'uploaded_by', 'uploaded_by_email', 'upload_source', 'is_public',
            'access_level', 'description', 'tags', 'width', 'height', 'duration', 'thumbnail_path',
            'has_preview', 'respond_io_file_id', 'external_url', 'last_accessed', 'expires_at',
            'retention_policy', 'is_image', 'is_document', 'is_safe', 'is_expired', 'download_url', 'thumbnail_url'
        ]
        read_only_fields = ['id', 'file_path', 'file_hash', 'virus_scan_status', 'virus_scan_result', 'uploaded_by_email', 'file_size_human', 'is_image', 'is_document', 'is_safe', 'is_expired', 'download_url', 'thumbnail_url']

class FileUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['original_filename', 'content_type', 'file_type', 'file_size', 'file_path', 'description', 'tags', 'upload_source']

    def validate_file_size(self, value):
        if value > 5 * 1024 * 1024:
            raise serializers.ValidationError('File size must be under 5MB for MVP.')
        return value

    def validate_content_type(self, value):
        allowed_types = ['image/jpeg', 'image/png', 'application/pdf']
        if value not in allowed_types:
            raise serializers.ValidationError('Only JPG, PNG, and PDF files are allowed for MVP.')
        return value

class FileMetadataSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = [
            'id', 'original_filename', 'file_type', 'file_size', 'uploaded_by', 'upload_source',
            'description', 'tags', 'width', 'height', 'duration', 'has_preview', 'last_accessed', 'expires_at'
        ]
        read_only_fields = fields 