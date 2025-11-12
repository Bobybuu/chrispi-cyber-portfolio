#blog/views.py
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Q
from .models import Article, Tag
from .serializers import (
    ArticleListSerializer, ArticleDetailSerializer, 
    ArticleCreateSerializer, TagSerializer
)


class ArticleListView(generics.ListAPIView):
    serializer_class = ArticleListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['tags__slug', 'author__id']
    search_fields = ['title', 'excerpt', 'sanitized_content', 'tags__name']
    ordering_fields = ['published_at', 'created_at', 'read_time']
    ordering = ['-published_at']

    def get_queryset(self):
        queryset = Article.objects.filter(
            is_published=True,
            published_at__lte=timezone.now()
        ).select_related('author').prefetch_related('tags')
        
        # Filter by tag name if provided
        tag_slug = self.request.query_params.get('tag', None)
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
        
        # Filter by author username if provided
        author_username = self.request.query_params.get('author', None)
        if author_username:
            queryset = queryset.filter(author__username=author_username)
        
        return queryset

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'status': 'success',
            'data': {
                'results': response.data,
                'count': self.get_queryset().count()
            }
        })


class ArticleDetailView(generics.RetrieveAPIView):
    serializer_class = ArticleDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

    def get_queryset(self):
        if self.request.user.is_authenticated and self.request.user.is_admin:
            return Article.objects.all().select_related('author').prefetch_related('tags')
        return Article.objects.filter(
            is_published=True,
            published_at__lte=timezone.now()
        ).select_related('author').prefetch_related('tags')


class ArticleCreateView(generics.CreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({
            'status': 'success',
            'data': response.data
        }, status=status.HTTP_201_CREATED)


class ArticleUpdateView(generics.UpdateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleCreateSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'

    def get_queryset(self):
        if self.request.user.is_admin:
            return Article.objects.all()
        return Article.objects.filter(author=self.request.user)

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({
            'status': 'success',
            'data': response.data
        })


class ArticleDeleteView(generics.DestroyAPIView):
    queryset = Article.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'slug'

    def get_queryset(self):
        if self.request.user.is_admin:
            return Article.objects.all()
        return Article.objects.filter(author=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'status': 'success',
            'message': 'Article deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)


class TagListView(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return Response({
            'status': 'success',
            'data': response.data
        })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def article_search(request):
    """
    Site-wide search endpoint for articles
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
    
    if len(query) < 3:
        return Response({
            'status': 'error',
            'error': {
                'code': 'QUERY_TOO_SHORT',
                'message': 'Search query must be at least 3 characters long'
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    articles = Article.objects.filter(
        Q(is_published=True) &
        Q(published_at__lte=timezone.now()) &
        (
            Q(title__icontains=query) |
            Q(excerpt__icontains=query) |
            Q(sanitized_content__icontains=query) |
            Q(tags__name__icontains=query)
        )
    ).select_related('author').prefetch_related('tags').distinct()
    
    serializer = ArticleListSerializer(articles, many=True)
    
    return Response({
        'status': 'success',
        'data': {
            'results': serializer.data,
            'count': articles.count(),
            'query': query
        }
    })