#contact/urls.py
from django.urls import path
from .views import (
    ContactMessageCreateView, ContactMessageListView, ContactMessageDetailView,
    ContactMessageUpdateView, ContactMessageDeleteView, ContactSettingView,
    contact_form_config, contact_stats
)

app_name = 'contact'

urlpatterns = [
    # Public endpoints
    path('messages/create/', ContactMessageCreateView.as_view(), name='message-create'),
    path('config/', contact_form_config, name='form-config'),
    
    # Admin endpoints
    path('messages/', ContactMessageListView.as_view(), name='message-list'),
    path('messages/<uuid:pk>/', ContactMessageDetailView.as_view(), name='message-detail'),
    path('messages/<uuid:pk>/update/', ContactMessageUpdateView.as_view(), name='message-update'),
    path('messages/<uuid:pk>/delete/', ContactMessageDeleteView.as_view(), name='message-delete'),
    path('settings/', ContactSettingView.as_view(), name='settings'),
    path('stats/', contact_stats, name='stats'),
]