from django.db import models
from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from products.models import Product
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json

User = get_user_model()

class Order(models.Model):
    PENDING = 'P'
    SHIPPED = 'S'
    DELIVERED = 'D'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (SHIPPED, 'Shipped'),
        (DELIVERED, 'Delivered'),
    ]
    
    user = models.ForeignKey(User, related_name='orders', on_delete=models.CASCADE)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default=PENDING)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Order {self.id} by {self.user.email}'
    
    def save(self, *args, **kwargs):
        # Invalidate user's orders cache when order is updated
        cache.delete(f'user_orders_{self.user.id}')
        super().save(*args, **kwargs)
    
    @property
    def status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='order_items', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f'{self.quantity} x {self.product.name} in Order {self.order.id}'
    
    def save(self, *args, **kwargs):
        # Update product stock when order item is created
        if not self.pk:
            self.product.stock -= self.quantity
            self.product.save()
        super().save(*args, **kwargs)

@receiver(post_save, sender=Order)
def order_status_changed(sender, instance, created, **kwargs):
    if not created and instance.status in ['S', 'D']:  # If status changed to Shipped or Delivered
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'user_{instance.user.id}',
            {
                'type': 'order_status_update',
                'order_id': instance.id,
                'status': instance.status_display,
            }
        )