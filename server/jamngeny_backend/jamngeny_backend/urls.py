from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Root URL redirect to API docs
    path('', RedirectView.as_view(url='/api/docs/', permanent=False)),
    
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/blog/', include('blog.urls')),
    path('api/portfolio/', include('portfolio.urls')),
    path('api/content/', include('content.urls')),
    path('api/contact/', include('contact.urls')),
    path('api/files/', include('files.urls')),
    path('api/utils/', include('utils.urls')),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # Health check
    path('healthz/', lambda request: HttpResponse('OK'), name='health-check'),
]

# Serve media files in development
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)