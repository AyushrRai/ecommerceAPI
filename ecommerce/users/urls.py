from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    MyTokenObtainPairView,
    RegisterView,
    UserProfileView,
    UserDetailView,
    AuthRootView  
)

urlpatterns = [
    path('', AuthRootView.as_view(), name='auth-root'),  
    path('login/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('me/', UserDetailView.as_view(), name='user_detail'),
]