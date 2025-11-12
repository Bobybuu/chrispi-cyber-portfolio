from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import UserSerializer, UserLoginSerializer
from .models import User


class UserRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        # For now, only allow admin creation
        # Later we'll implement proper user registration
        return Response(
            {"error": "User registration is currently disabled. Contact admin."},
            status=status.HTTP_403_FORBIDDEN
        )


class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            
            user = authenticate(request, username=email, password=password)
            
            if user:
                refresh = RefreshToken.for_user(user)
                user_data = UserSerializer(user).data
                
                return Response({
                    'status': 'success',
                    'data': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh),
                        'user': user_data
                    }
                })
            
            return Response({
                'status': 'error',
                'error': {
                    'code': 'INVALID_CREDENTIALS',
                    'message': 'Invalid email or password'
                }
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response({
            'status': 'error',
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Invalid input',
                'details': serializer.errors
            }
        }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user_data = UserSerializer(request.user).data
        return Response({
            'status': 'success',
            'data': user_data
        })


class UserListView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response({
            'status': 'success',
            'data': serializer.data
        })