# utils/views.py
import time
import psutil
from datetime import timedelta
from django.db import connection, models
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings
from django.db.utils import OperationalError
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


from .models import AuditLog, SystemSetting, HealthCheck, APIRequestLog
from .serializers import (
    AuditLogListSerializer, AuditLogDetailSerializer,
    SystemSettingSerializer, SystemSettingPublicSerializer,
    HealthCheckSerializer, APIRequestLogSerializer,
    SystemStatsSerializer, HealthCheckResponseSerializer
)


class AuditLogListView(generics.ListAPIView):
    serializer_class = AuditLogListSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['action', 'entity', 'severity', 'is_successful']
    search_fields = ['description', 'entity_id', 'performed_by__email']
    ordering_fields = ['created_at', 'severity']
    ordering = ['-created_at']

    def get_queryset(self):
        return AuditLog.objects.all().select_related('performed_by')

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'status': 'success',
            'data': {
                'results': response.data,
                'count': self.get_queryset().count()
            }
        })


class AuditLogDetailView(generics.RetrieveAPIView):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogDetailSerializer
    permission_classes = [permissions.IsAdminUser]

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return Response({
            'status': 'success',
            'data': response.data
        })


class SystemSettingView(generics.RetrieveUpdateAPIView):
    queryset = SystemSetting.objects.all()
    serializer_class = SystemSettingSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_object(self):
        return SystemSetting.get_instance()

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return Response({
            'status': 'success',
            'data': response.data
        })

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({
            'status': 'success',
            'data': response.data
        })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def system_info(request):
    """Public system information endpoint"""
    settings = SystemSetting.get_instance()
    serializer = SystemSettingPublicSerializer(settings)
    
    # Add basic system info
    system_info = {
        'settings': serializer.data,
        'version': '1.0.0',  # You can make this dynamic
        'timestamp': timezone.now(),
        'environment': 'production' if not settings.DEBUG else 'development'
    }
    
    return Response({
        'status': 'success',
        'data': system_info
    })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    """Comprehensive health check endpoint"""
    start_time = time.time()
    checks = {}
    details = {}
    
    # Database check
    try:
        connection.ensure_connection()
        checks['database'] = True
        details['database'] = 'Connected successfully'
    except OperationalError as e:
        checks['database'] = False
        details['database'] = f'Connection failed: {str(e)}'
    
    # Cache check
    try:
        cache.set('health_check', 'ok', 60)
        cache_result = cache.get('health_check') == 'ok'
        checks['cache'] = cache_result
        details['cache'] = 'Working' if cache_result else 'Failed'
    except Exception as e:
        checks['cache'] = False
        details['cache'] = f'Cache error: {str(e)}'
    
    # Storage check (if using file-based storage)
    try:
        from django.core.files.storage import default_storage
        test_content = b'health_check_test'
        test_path = 'health_check_test.txt'
        default_storage.save(test_path, test_content)
        if default_storage.exists(test_path):
            default_storage.delete(test_path)
            checks['storage'] = True
            details['storage'] = 'File storage working'
        else:
            checks['storage'] = False
            details['storage'] = 'File storage test failed'
    except Exception as e:
        checks['storage'] = False
        details['storage'] = f'Storage error: {str(e)}'
    
    # System resources
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        details['system'] = {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'disk_percent': disk.percent,
            'memory_available_gb': round(memory.available / (1024 ** 3), 2),
            'disk_free_gb': round(disk.free / (1024 ** 3), 2)
        }
        checks['system_resources'] = cpu_percent < 90 and memory.percent < 90 and disk.percent < 90
    except Exception as e:
        checks['system_resources'] = False
        details['system'] = f'System check failed: {str(e)}'
    
    # Log the health check
    response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
    all_checks_passed = all(checks.values())
    
    HealthCheck.log_check(
        check_type='full',
        is_successful=all_checks_passed,
        response_time=response_time,
        error_message='' if all_checks_passed else 'One or more checks failed',
        metadata={'checks': checks, 'details': details}
    )
    
    # Prepare response
    response_data = {
        'status': 'healthy' if all_checks_passed else 'unhealthy',
        'timestamp': timezone.now(),
        'response_time': round(response_time, 2),
        'checks': checks,
        'details': details
    }
    
    serializer = HealthCheckResponseSerializer(response_data)
    
    if all_checks_passed:
        return Response({
            'status': 'success',
            'data': serializer.data
        })
    else:
        return Response({
            'status': 'error',
            'data': serializer.data
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def system_stats(request):
    """Get comprehensive system statistics"""
    from django.contrib.auth import get_user_model
    from blog.models import Article
    from portfolio.models import PortfolioItem
    from contact.models import ContactMessage
    from files.models import File
    
    User = get_user_model()
    
    # Basic counts
    stats = {
        'total_users': User.objects.count(),
        'total_articles': Article.objects.count(),
        'published_articles': Article.objects.filter(is_published=True).count(),
        'total_portfolio_items': PortfolioItem.objects.count(),
        'published_portfolio_items': PortfolioItem.objects.filter(is_published=True).count(),
        'total_contact_messages': ContactMessage.objects.count(),
        'unread_messages': ContactMessage.objects.filter(status='new').count(),
        'total_files': File.objects.count(),
        'total_file_size': File.objects.aggregate(total_size=models.Sum('file_size'))['total_size'] or 0,
        'total_audit_logs': AuditLog.objects.count(),
        'total_api_requests': APIRequestLog.objects.count(),
    }
    
    # Recent activity (last 7 days)
    seven_days_ago = timezone.now() - timedelta(days=7)
    stats.update({
        'recent_users': User.objects.filter(date_joined__gte=seven_days_ago).count(),
        'recent_articles': Article.objects.filter(created_at__gte=seven_days_ago).count(),
        'recent_portfolio_items': PortfolioItem.objects.filter(created_at__gte=seven_days_ago).count(),
        'recent_contact_messages': ContactMessage.objects.filter(created_at__gte=seven_days_ago).count(),
        'recent_files': File.objects.filter(created_at__gte=seven_days_ago).count(),
    })
    
    # System info
    import psutil
    stats.update({
        'system_uptime': psutil.boot_time(),
        'memory_usage_percent': psutil.virtual_memory().percent,
        'cpu_usage_percent': psutil.cpu_percent(interval=1),
        'disk_usage_percent': psutil.disk_usage('/').percent,
    })
    
    # Database size (PostgreSQL specific)
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT pg_size_pretty(pg_database_size(%s))
            """, [settings.DATABASES['default']['NAME']])
            db_size = cursor.fetchone()[0]
            stats['database_size'] = db_size
    except Exception:
        stats['database_size'] = 'Unknown'
    
    serializer = SystemStatsSerializer(stats)
    return Response({
        'status': 'success',
        'data': serializer.data
    })


class APIRequestLogListView(generics.ListAPIView):
    serializer_class = APIRequestLogSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['method', 'status_code', 'is_authenticated']
    search_fields = ['path', 'user__email', 'ip_address']
    ordering_fields = ['created_at', 'response_time', 'status_code']
    ordering = ['-created_at']

    def get_queryset(self):
        return APIRequestLog.objects.all().select_related('user')

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'status': 'success',
            'data': {
                'results': response.data,
                'count': self.get_queryset().count()
            }
        })


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def api_analytics(request):
    """Get API analytics and metrics"""
    # Time range for analytics (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    # Basic metrics
    total_requests = APIRequestLog.objects.filter(created_at__gte=thirty_days_ago).count()
    successful_requests = APIRequestLog.objects.filter(
        created_at__gte=thirty_days_ago, status_code__lt=400
    ).count()
    error_requests = APIRequestLog.objects.filter(
        created_at__gte=thirty_days_ago, status_code__gte=400
    ).count()
    
    # Response time statistics
    response_times = APIRequestLog.objects.filter(
        created_at__gte=thirty_days_ago
    ).aggregate(
        avg_response_time=models.Avg('response_time'),
        max_response_time=models.Max('response_time'),
        min_response_time=models.Min('response_time')
    )
    
    # Most frequent endpoints
    frequent_endpoints = APIRequestLog.objects.filter(
        created_at__gte=thirty_days_ago
    ).values('path', 'method').annotate(
        count=models.Count('id'),
        avg_time=models.Avg('response_time')
    ).order_by('-count')[:10]
    
    # Error breakdown
    error_breakdown = APIRequestLog.objects.filter(
        created_at__gte=thirty_days_ago, status_code__gte=400
    ).values('status_code').annotate(count=models.Count('id')).order_by('-count')
    
    analytics = {
        'time_period': 'last_30_days',
        'total_requests': total_requests,
        'successful_requests': successful_requests,
        'error_requests': error_requests,
        'success_rate': round((successful_requests / total_requests * 100), 2) if total_requests > 0 else 0,
        'response_times': {
            'average': round(response_times['avg_response_time'] or 0, 2),
            'max': round(response_times['max_response_time'] or 0, 2),
            'min': round(response_times['min_response_time'] or 0, 2),
        },
        'frequent_endpoints': list(frequent_endpoints),
        'error_breakdown': list(error_breakdown),
    }
    
    return Response({
        'status': 'success',
        'data': analytics
    })