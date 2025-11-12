from django.urls import path
from .views import (
    FileListView, FileDetailView, FileDownloadView, FileCreateView,
    FileUpdateView, FileDeleteView, PresignedUploadView,
    upload_complete, file_stats
)

app_name = 'files'

urlpatterns = [
    # File management
    path('files/', FileListView.as_view(), name='file-list'),
    path('files/create/', FileCreateView.as_view(), name='file-create'),
    path('files/<uuid:pk>/', FileDetailView.as_view(), name='file-detail'),
    path('files/<uuid:pk>/download/', FileDownloadView.as_view(), name='file-download'),
    path('files/<uuid:pk>/update/', FileUpdateView.as_view(), name='file-update'),
    path('files/<uuid:pk>/delete/', FileDeleteView.as_view(), name='file-delete'),
    
    # Upload endpoints
    path('upload/presign/', PresignedUploadView.as_view(), name='upload-presign'),
    path('upload-complete/', upload_complete, name='upload-complete'),
    
    # Stats
    path('stats/', file_stats, name='file-stats'),
]