from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.http import Http404
from .models import About, Service
from .serializers import (
    AboutSerializer, AboutUpdateSerializer,
    ServiceListSerializer, ServiceDetailSerializer, ServiceCreateSerializer
)


class AboutDetailView(generics.RetrieveAPIView):
    serializer_class = AboutSerializer
    permission_classes = [permissions.AllowAny]

    def get_object(self):
        try:
            return About.objects.get()
        except About.DoesNotExist:
            # Return a default About instance if none exists
            return About(
                name="Robert Jamngeny",
                title="ICT & Cybersecurity Specialist",
                sanitized_bio="Connecting Technology, Strategy, and Storytelling for a Secure Digital Future.",
                experience_years=15
            )

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'status': 'success',
            'data': serializer.data
        })


class AboutUpdateView(generics.UpdateAPIView):
    queryset = About.objects.all()
    serializer_class = AboutUpdateSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_object(self):
        # Get or create the singleton instance
        about, created = About.objects.get_or_create(
            defaults={
                'name': 'Robert Jamngeny',
                'title': 'ICT & Cybersecurity Specialist',
                'bio': 'Connecting Technology, Strategy, and Storytelling for a Secure Digital Future.'
            }
        )
        return about

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({
            'status': 'success',
            'data': response.data
        })


class ServiceListView(generics.ListAPIView):
    serializer_class = ServiceListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        queryset = Service.objects.filter(is_published=True)
        
        # Filter featured services if requested
        featured_only = self.request.query_params.get('featured', '').lower() == 'true'
        if featured_only:
            queryset = queryset.filter(is_featured=True)
        
        return queryset.order_by('order', 'title')

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'status': 'success',
            'data': response.data
        })


class ServiceDetailView(generics.RetrieveAPIView):
    serializer_class = ServiceDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.is_admin:
            return Service.objects.all()
        return Service.objects.filter(is_published=True)


class ServiceCreateView(generics.CreateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({
            'status': 'success',
            'data': response.data
        }, status=status.HTTP_201_CREATED)


class ServiceUpdateView(generics.UpdateAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'

    def get_queryset(self):
        if self.request.user.is_admin:
            return Service.objects.all()
        return Service.objects.all()  # Editors can also update services

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({
            'status': 'success',
            'data': response.data
        })


class ServiceDeleteView(generics.DestroyAPIView):
    queryset = Service.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'

    def get_queryset(self):
        if self.request.user.is_admin:
            return Service.objects.all()
        return Service.objects.all()  # Editors can also delete services

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'status': 'success',
            'message': 'Service deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)


class FeaturedServicesView(generics.ListAPIView):
    serializer_class = ServiceListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        return Service.objects.filter(
            is_published=True,
            is_featured=True
        ).order_by('order', 'title')[:6]  # Limit to 6 featured services

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'status': 'success',
            'data': response.data
        })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def services_count(request):
    """Get count of published services"""
    count = Service.objects.filter(is_published=True).count()
    return Response({
        'status': 'success',
        'data': {
            'count': count
        }
    })