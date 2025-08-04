from rest_framework import generics, permissions, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer, ProductStockSerializer

from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer, ProductStockSerializer

class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        # Try to get from cache first
        cached_data = cache.get('categories_list')
        if cached_data is not None:
            return cached_data
        
        # If not in cache, get from database and cache it
        queryset = super().get_queryset()
        cache.set('categories_list', queryset, timeout=60*60)  # Cache for 1 hour
        return queryset

class CategoryRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAdminUser]

class ProductListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'in_stock']
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'created_at']
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]
    
    @method_decorator(cache_page(60*60))  # Cache for 1 hour
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def get_queryset(self):
        # Try to get from cache first
        cached_data = cache.get('products_list')
        if cached_data is not None:
            return cached_data
        
        # If not in cache, get from database and cache it
        queryset = Product.objects.select_related('category').filter(stock__gt=0)
        cache.set('products_list', queryset, timeout=60*60)  # Cache for 1 hour
        return queryset

class ProductRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.select_related('category')
    serializer_class = ProductSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]
    
    @method_decorator(cache_page(60*60))  # Cache for 1 hour
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)
    
    def get_object(self):
        # Try to get from cache first
        obj_id = self.kwargs.get('pk')
        cached_data = cache.get(f'product_{obj_id}')
        if cached_data is not None:
            return cached_data
        
        # If not in cache, get from database and cache it
        obj = super().get_object()
        cache.set(f'product_{obj_id}', obj, timeout=60*60)  # Cache for 1 hour
        return obj

class ProductStockUpdateView(generics.UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductStockSerializer
    permission_classes = [permissions.IsAdminUser]
    http_method_names = ['patch']
    
    def perform_update(self, serializer):
        instance = serializer.save()
        # Invalidate cache for this product and products list
        cache.delete(f'product_{instance.id}')
        cache.delete('products_list')





