"""
File upload/download API endpoints.
"""

from rest_framework import viewsets, status, permissions, parsers
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import File
from .serializers import FileSerializer, FileUploadSerializer, FileMetadataSerializer
from apps.authentication.permissions import IsSystemAdmin, IsManagerOrSystemAdmin, IsAssignedUserOrManager
from django.utils.translation import gettext_lazy as _

class FileViewSet(viewsets.ModelViewSet):
    """
    API endpoints for file upload/download with validation.
    """
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def get_queryset(self):
        user = self.request.user
        if user.is_system_admin or user.is_manager:
            return File.objects.all()
        else:
            return File.objects.filter(uploaded_by=user)

    @extend_schema(
        summary="Upload file",
        description="Upload a file with type/size validation."
    )
    @action(detail=False, methods=['post'], serializer_class=FileUploadSerializer, parser_classes=[parsers.MultiPartParser, parsers.FormParser])
    def upload(self, request):
        serializer = FileUploadSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        file_obj = serializer.save(uploaded_by=request.user)
        return Response(FileSerializer(file_obj).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Download file",
        description="Download a file with access control."
    )
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        file_obj = self.get_object()
        # Access control logic here (MVP: allow if user is uploader or assigned to conversation)
        # For MVP, just return file metadata
        return Response(FileSerializer(file_obj).data)

    @extend_schema(
        summary="Get file metadata",
        description="Retrieve file metadata."
    )
    @action(detail=True, methods=['get'], url_path='metadata')
    def metadata(self, request, pk=None):
        file_obj = self.get_object()
        serializer = FileMetadataSerializer(file_obj)
        return Response(serializer.data)

    @extend_schema(
        summary="Get virus scan status",
        description="Get virus scan status for a file (stub for MVP)."
    )
    @action(detail=True, methods=['get'], url_path='virus-scan-status')
    def virus_scan_status(self, request, pk=None):
        file_obj = self.get_object()
        return Response({'file_id': str(file_obj.id), 'virus_scan_status': file_obj.virus_scan_status, 'virus_scan_result': file_obj.virus_scan_result}) 