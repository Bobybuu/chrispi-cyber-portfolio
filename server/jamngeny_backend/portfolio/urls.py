#portfolio/urls.py
from django.urls import path
from .views import (
    PortfolioCategoryListView, PortfolioItemListView, PortfolioItemDetailView,
    PortfolioItemCreateView, PortfolioItemUpdateView, PortfolioItemDeleteView,
    FeaturedPortfolioView, portfolio_search
)

app_name = 'portfolio'

urlpatterns = [
    # Public endpoints
    path('categories/', PortfolioCategoryListView.as_view(), name='category-list'),
    path('items/', PortfolioItemListView.as_view(), name='item-list'),
    path('items/featured/', FeaturedPortfolioView.as_view(), name='featured-items'),
    path('items/<slug:slug>/', PortfolioItemDetailView.as_view(), name='item-detail'),
    path('search/', portfolio_search, name='portfolio-search'),
    
    # Protected endpoints
    path('items/create/', PortfolioItemCreateView.as_view(), name='item-create'),
    path('items/<slug:slug>/update/', PortfolioItemUpdateView.as_view(), name='item-update'),
    path('items/<slug:slug>/delete/', PortfolioItemDeleteView.as_view(), name='item-delete'),
]