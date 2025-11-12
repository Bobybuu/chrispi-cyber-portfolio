#blog/urls.py
from django.urls import path
from .views import (
    ArticleListView, ArticleDetailView, ArticleCreateView,
    ArticleUpdateView, ArticleDeleteView, TagListView, article_search
)

app_name = 'blog'

urlpatterns = [
    # Public endpoints
    path('articles/', ArticleListView.as_view(), name='article-list'),
    path('articles/<slug:slug>/', ArticleDetailView.as_view(), name='article-detail'),
    path('tags/', TagListView.as_view(), name='tag-list'),
    path('search/', article_search, name='article-search'),
    
    # Protected endpoints
    path('articles/create/', ArticleCreateView.as_view(), name='article-create'),
    path('articles/<slug:slug>/update/', ArticleUpdateView.as_view(), name='article-update'),
    path('articles/<slug:slug>/delete/', ArticleDeleteView.as_view(), name='article-delete'),
]