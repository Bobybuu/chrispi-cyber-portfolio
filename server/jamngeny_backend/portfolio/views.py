from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from .models import PortfolioCategory, PortfolioItem
from .serializers import (
    PortfolioCategorySerializer, PortfolioItemListSerializer,
    PortfolioItemDetailSerializer, PortfolioItemCreateSerializer
)


class PortfolioCategoryListView(generics.ListAPIView):
    serializer_class = PortfolioCategorySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        return PortfolioCategory.objects.filter(is_active=True).prefetch_related('portfolio_items')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'status': 'success',
            'data': response.data
        })


class PortfolioItemListView(generics.ListAPIView):
    serializer_class = PortfolioItemListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category__slug', 'is_featured']
    search_fields = ['title', 'summary', 'client', 'technologies']
    ordering_fields = ['project_date', 'created_at', 'is_featured']
    ordering = ['-is_featured', '-project_date']

    def get_queryset(self):
        queryset = PortfolioItem.objects.filter(
            is_published=True
        ).select_related('category').prefetch_related('secondary_categories', 'images')
        
        # Filter by category slug if provided
        category_slug = self.request.query_params.get('category', None)
        if category_slug:
            queryset = queryset.filter(
                Q(category__slug=category_slug) | 
                Q(secondary_categories__slug=category_slug)
            ).distinct()
        
        # Filter by technology if provided
        technology = self.request.query_params.get('technology', None)
        if technology:
            queryset = queryset.filter(technologies__contains=[technology])
        
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'status': 'success',
            'data': {
                'results': response.data,
                'count': self.get_queryset().count()
            }
        })


class PortfolioItemDetailView(generics.RetrieveAPIView):
    serializer_class = PortfolioItemDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.is_admin:
            return PortfolioItem.objects.all().select_related('category').prefetch_related(
                'secondary_categories', 'images'
            )
        return PortfolioItem.objects.filter(
            is_published=True
        ).select_related('category').prefetch_related('secondary_categories', 'images')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class PortfolioItemCreateView(generics.CreateAPIView):
    queryset = PortfolioItem.objects.all()
    serializer_class = PortfolioItemCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({
            'status': 'success',
            'data': response.data
        }, status=status.HTTP_201_CREATED)


class PortfolioItemUpdateView(generics.UpdateAPIView):
    queryset = PortfolioItem.objects.all()
    serializer_class = PortfolioItemCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'

    def get_queryset(self):
        if self.request.user.is_admin:
            return PortfolioItem.objects.all()
        return PortfolioItem.objects.all()

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({
            'status': 'success',
            'data': response.data
        })


class PortfolioItemDeleteView(generics.DestroyAPIView):
    queryset = PortfolioItem.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'

    def get_queryset(self):
        if self.request.user.is_admin:
            return PortfolioItem.objects.all()
        return PortfolioItem.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'status': 'success',
            'message': 'Portfolio item deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)


class FeaturedPortfolioView(generics.ListAPIView):
    serializer_class = PortfolioItemListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        return PortfolioItem.objects.filter(
            is_published=True,
            is_featured=True
        ).select_related('category').prefetch_related('images')[:6]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'status': 'success',
            'data': response.data
        })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def portfolio_search(request):
    """
    Search endpoint for portfolio items
    """
    query = request.query_params.get('q', '').strip()
    
    if not query:
        return Response({
            'status': 'error',
            'error': {
                'code': 'MISSING_QUERY',
                'message': 'Search query parameter "q" is required'
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if len(query) < 2:
        return Response({
            'status': 'error',
            'error': {
                'code': 'QUERY_TOO_SHORT',
                'message': 'Search query must be at least 2 characters long'
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    portfolio_items = PortfolioItem.objects.filter(
        is_published=True
    ).filter(
        Q(title__icontains=query) |
        Q(summary__icontains=query) |
        Q(client__icontains=query) |
        Q(technologies__icontains=query) |
        Q(category__name__icontains=query)
    ).select_related('category').prefetch_related('images').distinct()
    
    serializer = PortfolioItemListSerializer(portfolio_items, many=True, context={'request': request})
    
    return Response({
        'status': 'success',
        'data': {
            'results': serializer.data,
            'count': portfolio_items.count(),
            'query': query
        }
    })