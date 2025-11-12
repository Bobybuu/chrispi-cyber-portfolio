# content/urls.py
from django.urls import path
from .views import (
    AboutDetailView, AboutUpdateView,
    ServiceListView, ServiceDetailView, ServiceCreateView,
    ServiceUpdateView, ServiceDeleteView, FeaturedServicesView,
    services_count
)

app_name = 'content'

urlpatterns = [
    # About endpoints
    path('about/', AboutDetailView.as_view(), name='about-detail'),
    path('about/update/', AboutUpdateView.as_view(), name='about-update'),
    
    # Service endpoints
    path('services/', ServiceListView.as_view(), name='service-list'),
    path('services/featured/', FeaturedServicesView.as_view(), name='featured-services'),
    path('services/count/', services_count, name='services-count'),
    path('services/<slug:slug>/', ServiceDetailView.as_view(), name='service-detail'),
    
    # Protected service endpoints
    path('services/create/', ServiceCreateView.as_view(), name='service-create'),
    path('services/<slug:slug>/update/', ServiceUpdateView.as_view(), name='service-update'),
    path('services/<slug:slug>/delete/', ServiceDeleteView.as_view(), name='service-delete'),
]