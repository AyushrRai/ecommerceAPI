from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer, RegisterSerializer, UserSerializer, UserProfileSerializer
from .models import User, UserProfile
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
    
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

class UserDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @method_decorator(cache_page(60*60))  # Cache for 1 hour
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
    def get_object(self):
        return self.request.user
    


from rest_framework.views import APIView  
from rest_framework.response import Response
from rest_framework.reverse import reverse

class AuthRootView(APIView):
    """View to list all available auth endpoints"""
    def get(self, request, format=None):
        return Response({
            'login': reverse('token_obtain_pair', request=request),
            'token-refresh': reverse('token_refresh', request=request),
            'register': reverse('auth_register', request=request),
            'profile': reverse('user_profile', request=request),
            'user-details': reverse('user_detail', request=request),
        })