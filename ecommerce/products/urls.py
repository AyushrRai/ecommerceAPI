from django.urls import path
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .views import (
    CategoryListCreateView,
    CategoryRetrieveUpdateDestroyView,
    ProductListCreateView,
    ProductRetrieveUpdateDestroyView,
    ProductStockUpdateView
)

class ProductsRootView(APIView):
    def get(self, request, format=None):
        return Response({
            'categories': reverse('category-list', request=request),
            'products': reverse('product-list', request=request),
        })

urlpatterns = [
    path('', ProductsRootView.as_view(), name='products-root'),
    path('categories/', CategoryListCreateView.as_view(), name='category-list'),
    path('categories/<int:pk>/', CategoryRetrieveUpdateDestroyView.as_view(), name='category-detail'),
    path('products/', ProductListCreateView.as_view(), name='product-list'),
    path('products/<int:pk>/', ProductRetrieveUpdateDestroyView.as_view(), name='product-detail'),
    path('products/<int:pk>/stock/', ProductStockUpdateView.as_view(), name='product-stock-update'),
]