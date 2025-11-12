import uuid
import json
from datetime import timedelta
from django.db import models  # ADD THIS IMPORT
from django.conf import settings
from django.utils import timezone
from django.core.files.storage import default_storage
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import File, FileUploadRequest
from .serializers import (
    FileListSerializer, FileDetailSerializer, FileCreateSerializer,
    FileUpdateSerializer, FileUploadRequestSerializer,
    PresignedUploadResponseSerializer, FileUploadCompleteSerializer
)


class FileListView(generics.ListAPIView):
    serializer_class = FileListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'is_public', 'is_approved', 'is_featured']
    search_fields = ['original_filename', 'title', 'description', 'tags']
    ordering_fields = ['created_at', 'file_size', 'download_count']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin:
            # Admins can see all files
            return File.objects.all().select_related('uploaded_by')
        else:
            # Users can see public files and their own files
            return File.objects.filter(
                models.Q(is_public=True) | models.Q(uploaded_by=user)
            ).filter(is_approved=True).select_related('uploaded_by')

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'status': 'success',
            'data': {
                'results': response.data,
                'count': self.get_queryset().count()
            }
        })


class FileDetailView(generics.RetrieveAPIView):
    serializer_class = FileDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin:
            return File.objects.all().select_related('uploaded_by')
        else:
            return File.objects.filter(
                models.Q(is_public=True) | models.Q(uploaded_by=user)
            ).filter(is_approved=True).select_related('uploaded_by')

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return Response({
            'status': 'success',
            'data': response.data
        })


class FileDownloadView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin:
            return File.objects.all()
        else:
            return File.objects.filter(
                models.Q(is_public=True) | models.Q(uploaded_by=user)
            ).filter(is_approved=True)

    def retrieve(self, request, *args, **kwargs):
        file_obj = self.get_object()
        
        # Check access permissions
        if not file_obj.can_access(request.user):
            return Response({
                'status': 'error',
                'error': {
                    'code': 'PERMISSION_DENIED',
                    'message': 'You do not have permission to access this file.'
                }
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Increment download count
        file_obj.increment_download_count()
        
        # Return file URL for download
        return Response({
            'status': 'success',
            'data': {
                'download_url': file_obj.file_url,
                'filename': file_obj.original_filename,
                'mime_type': file_obj.mime_type,
                'size': file_obj.file_size
            }
        })


class FileCreateView(generics.CreateAPIView):
    queryset = File.objects.all()
    serializer_class = FileCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({
            'status': 'success',
            'data': response.data
        }, status=status.HTTP_201_CREATED)


class FileUpdateView(generics.UpdateAPIView):
    queryset = File.objects.all()
    serializer_class = FileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin:
            return File.objects.all()
        else:
            return File.objects.filter(uploaded_by=user)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({
            'status': 'success',
            'data': response.data
        })


class FileDeleteView(generics.DestroyAPIView):
    queryset = File.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        
        if user.is_admin:
            return File.objects.all()
        else:
            return File.objects.filter(uploaded_by=user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Delete the actual file from storage
        if instance.file:
            instance.file.delete(save=False)
        
        self.perform_destroy(instance)
        return Response({
            'status': 'success',
            'message': 'File deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)


class PresignedUploadView(generics.CreateAPIView):
    serializer_class = FileUploadRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'status': 'error',
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Invalid upload request',
                    'details': serializer.errors
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create upload request
        upload_request = FileUploadRequest(
            uploaded_by=request.user,
            original_filename=serializer.validated_data['original_filename'],
            file_size=serializer.validated_data['file_size'],
            mime_type=serializer.validated_data.get('mime_type', 'application/octet-stream'),
            file_extension=serializer.validated_data['file_extension'],
            purpose=serializer.validated_data.get('purpose', ''),
            upload_token=str(uuid.uuid4()),
            expires_at=timezone.now() + timedelta(hours=1)  # 1 hour expiry
        )
        upload_request.save()
        
        # Generate presigned URL data (simplified - in production, use your storage backend's presigned URL feature)
        # For Django's default storage, we'll return the token and let the client upload directly
        # In production with S3, you would generate actual presigned POST data here
        
        response_data = {
            'upload_token': upload_request.upload_token,
            'upload_url': f'/api/files/upload-complete/',  # Endpoint to complete upload
            'expires_at': upload_request.expires_at,
            'fields': {
                'upload_token': upload_request.upload_token,
            }
        }
        
        response_serializer = PresignedUploadResponseSerializer(response_data)
        return Response({
            'status': 'success',
            'data': response_serializer.data
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upload_complete(request):
    """Complete the upload process after file has been uploaded"""
    serializer = FileUploadCompleteSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'status': 'error',
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid upload completion data',
                'details': serializer.errors
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        upload_token = serializer.validated_data['upload_token']
        file_data = serializer.validated_data['file_data']
        
        # Get upload request
        upload_request = FileUploadRequest.objects.get(
            upload_token=upload_token,
            uploaded_by=request.user
        )
        
        if not upload_request.is_valid:
            return Response({
                'status': 'error',
                'error': {
                    'code': 'INVALID_TOKEN',
                    'message': 'Upload token is invalid or expired'
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Mark upload request as used
        upload_request.is_used = True
        
        # Create file record (in a real implementation, you'd have the actual file)
        # This is a simplified version - in production, you'd move the uploaded file
        # to its final location and create the File record
        
        file_serializer = FileCreateSerializer(data=file_data, context={'request': request})
        if file_serializer.is_valid():
            file_obj = file_serializer.save()
            upload_request.resulting_file = file_obj
            upload_request.save()
            
            return Response({
                'status': 'success',
                'data': FileDetailSerializer(file_obj).data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'status': 'error',
                'error': {
                    'code': 'FILE_VALIDATION_ERROR',
                    'message': 'Invalid file data',
                    'details': file_serializer.errors
                }
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except FileUploadRequest.DoesNotExist:
        return Response({
            'status': 'error',
            'error': {
                'code': 'TOKEN_NOT_FOUND',
                'message': 'Upload token not found'
            }
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def file_stats(request):
    """Get file statistics for admin dashboard"""
    total_files = File.objects.count()
    total_size = File.objects.aggregate(total_size=models.Sum('file_size'))['total_size'] or 0
    public_files = File.objects.filter(is_public=True).count()
    unapproved_files = File.objects.filter(is_approved=False).count()
    
    # Files by category
    category_counts = {}
    for category_value, category_label in File.FILE_CATEGORIES:
        category_counts[category_value] = File.objects.filter(category=category_value).count()
    
    # Recent uploads (last 7 days)
    seven_days_ago = timezone.now() - timedelta(days=7)
    recent_uploads = File.objects.filter(created_at__gte=seven_days_ago).count()
    
    # Top downloaded files
    top_downloaded = File.objects.order_by('-download_count')[:5].values(
        'original_filename', 'download_count'
    )
    
    return Response({
        'status': 'success',
        'data': {
            'total_files': total_files,
            'total_size': total_size,
            'total_size_display': f"{total_size / (1024 * 1024 * 1024):.2f} GB",
            'public_files': public_files,
            'unapproved_files': unapproved_files,
            'recent_uploads_7d': recent_uploads,
            'category_breakdown': category_counts,
            'top_downloaded': list(top_downloaded),
        }
    })