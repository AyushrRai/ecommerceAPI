from django.urls import path
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from .views import (
    OrderListCreateView,
    OrderRetrieveView,
    OrderStatusUpdateView
)

class OrdersRootView(APIView):
    def get(self, request, format=None):
        return Response({
            'orders': reverse('order-list', request=request),
            'documentation': 'See API documentation for details'
        })

urlpatterns = [
    path('', OrdersRootView.as_view(), name='orders-root'),
    path('orders/', OrderListCreateView.as_view(), name='order-list'),
    path('orders/<int:pk>/', OrderRetrieveView.as_view(), name='order-detail'),
    path('orders/<int:pk>/status/', OrderStatusUpdateView.as_view(), name='order-status-update'),
]