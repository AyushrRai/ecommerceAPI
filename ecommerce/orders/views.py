from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .models import Order
from .serializers import OrderSerializer, OrderStatusSerializer

class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Try to get from cache first
        cached_data = cache.get(f'user_orders_{self.request.user.id}')
        if cached_data is not None:
            return cached_data
        
        # If not in cache, get from database and cache it
        queryset = Order.objects.filter(user=self.request.user).prefetch_related('items__product')
        cache.set(f'user_orders_{self.request.user.id}', queryset, timeout=60*60)  # Cache for 1 hour
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class OrderRetrieveView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product')

class OrderStatusUpdateView(generics.UpdateAPIView):
    serializer_class = OrderStatusSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Order.objects.all()
    http_method_names = ['patch']
    
    def perform_update(self, serializer):
        instance = serializer.save()
        # Invalidate user's orders cache
        cache.delete(f'user_orders_{instance.user.id}')