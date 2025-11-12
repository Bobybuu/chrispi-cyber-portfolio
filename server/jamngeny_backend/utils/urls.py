# utils/urls.py
from django.urls import path
from . import views

app_name = 'utils'

urlpatterns = [
    # Audit Logs
    path('audit-logs/', views.AuditLogListView.as_view(), name='audit-log-list'),
    path('audit-logs/<uuid:pk>/', views.AuditLogDetailView.as_view(), name='audit-log-detail'),
    
    # System Settings
    path('system-settings/', views.SystemSettingView.as_view(), name='system-settings'),
    path('system-info/', views.system_info, name='system-info'),
    
    # Health & Monitoring
    path('health/', views.health_check, name='health-check'),
    path('stats/', views.system_stats, name='system-stats'),
    
    # API Analytics
    path('api-logs/', views.APIRequestLogListView.as_view(), name='api-log-list'),
    path('api-analytics/', views.api_analytics, name='api-analytics'),
]