#contact/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings
from .models import ContactMessage, ContactSetting
from .serializers import (
    ContactMessageCreateSerializer, ContactMessageListSerializer,
    ContactMessageDetailSerializer, ContactMessageUpdateSerializer,
    ContactSettingSerializer, ContactFormConfigSerializer
)


class ContactMessageCreateView(generics.CreateAPIView):
    serializer_class = ContactMessageCreateSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        # Get contact settings
        contact_settings = ContactSetting.get_instance()
        
        # Check if contact form is enabled
        if not contact_settings.is_contact_form_enabled:
            return Response({
                'status': 'error',
                'error': {
                    'code': 'FORM_DISABLED',
                    'message': 'Contact form is currently disabled. Please try again later.'
                }
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # Rate limiting
        if contact_settings.rate_limit_enabled:
            ip_address = self.get_client_ip(request)
            cache_key = f'contact_rate_limit_{ip_address}'
            request_count = cache.get(cache_key, 0)
            
            if request_count >= contact_settings.rate_limit_count:
                return Response({
                    'status': 'error',
                    'error': {
                        'code': 'RATE_LIMITED',
                        'message': 'Too many contact attempts. Please try again later.'
                    }
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        # Validate required fields
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'status': 'error',
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': 'Please check your input',
                    'details': serializer.errors
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Create the message
        try:
            self.perform_create(serializer)
            
            # Update rate limit counter
            if contact_settings.rate_limit_enabled:
                cache_key = f'contact_rate_limit_{ip_address}'
                cache.set(cache_key, request_count + 1, contact_settings.rate_limit_period)
            
            # TODO: Send notifications if enabled
            # TODO: Send auto-response if enabled
            
            return Response({
                'status': 'success',
                'message': 'Thank you for your message. We will get back to you soon.',
                'data': {
                    'id': str(serializer.instance.id)
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'error': {
                    'code': 'SERVER_ERROR',
                    'message': 'An error occurred while sending your message. Please try again.'
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_create(self, serializer):
        serializer.save(source='website')

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ContactMessageListView(generics.ListAPIView):
    serializer_class = ContactMessageListSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'priority', 'source', 'category', 'is_processed']
    search_fields = ['name', 'email', 'subject', 'message', 'company']
    ordering_fields = ['created_at', 'updated_at', 'priority']
    ordering = ['-created_at']

    def get_queryset(self):
        return ContactMessage.objects.all().select_related('assigned_to')

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'status': 'success',
            'data': {
                'results': response.data,
                'count': self.get_queryset().count()
            }
        })


class ContactMessageDetailView(generics.RetrieveAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageDetailSerializer
    permission_classes = [permissions.IsAdminUser]

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return Response({
            'status': 'success',
            'data': response.data
        })


class ContactMessageUpdateView(generics.UpdateAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageUpdateSerializer
    permission_classes = [permissions.IsAdminUser]

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({
            'status': 'success',
            'data': response.data
        })


class ContactMessageDeleteView(generics.DestroyAPIView):
    queryset = ContactMessage.objects.all()
    permission_classes = [permissions.IsAdminUser]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'status': 'success',
            'message': 'Contact message deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)


class ContactSettingView(generics.RetrieveUpdateAPIView):
    queryset = ContactSetting.objects.all()
    serializer_class = ContactSettingSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_object(self):
        return ContactSetting.get_instance()

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
def contact_form_config(request):
    """Public endpoint for contact form configuration"""
    settings = ContactSetting.get_instance()
    
    config = {
        'is_enabled': settings.is_contact_form_enabled,
        'required_fields': {
            'name': settings.require_name,
            'email': settings.require_email,
            'phone': settings.require_phone,
            'company': settings.require_company,
            'subject': settings.require_subject,
        },
        'categories': settings.available_categories or ['general'],
        'recaptcha_enabled': settings.recaptcha_enabled,
        'recaptcha_site_key': settings.recaptcha_site_key if settings.recaptcha_enabled else '',
    }
    
    serializer = ContactFormConfigSerializer(config)
    return Response({
        'status': 'success',
        'data': serializer.data
    })


@api_view(['GET'])
@permission_classes([permissions.IsAdminUser])
def contact_stats(request):
    """Get contact message statistics for admin dashboard"""
    total_messages = ContactMessage.objects.count()
    new_messages = ContactMessage.objects.filter(status='new').count()
    unprocessed_messages = ContactMessage.objects.filter(is_processed=False).count()
    
    # Messages by status
    status_counts = {}
    for status_value, status_label in ContactMessage.STATUS_CHOICES:
        status_counts[status_value] = ContactMessage.objects.filter(status=status_value).count()
    
    # Messages by source
    source_counts = {}
    for source_value, source_label in ContactMessage.SOURCE_CHOICES:
        source_counts[source_value] = ContactMessage.objects.filter(source=source_value).count()
    
    # Recent activity (last 30 days)
    thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
    recent_messages = ContactMessage.objects.filter(created_at__gte=thirty_days_ago).count()
    
    return Response({
        'status': 'success',
        'data': {
            'total_messages': total_messages,
            'new_messages': new_messages,
            'unprocessed_messages': unprocessed_messages,
            'recent_messages_30d': recent_messages,
            'status_breakdown': status_counts,
            'source_breakdown': source_counts,
        }
    })