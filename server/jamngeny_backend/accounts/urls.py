from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import UserLoginView, UserProfileView, UserListView

app_name = 'accounts'

urlpatterns = [
    path('auth/login/', UserLoginView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', UserProfileView.as_view(), name='profile'),
    path('users/', UserListView.as_view(), name='user-list'),
]