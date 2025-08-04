from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.core.cache import cache

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Invalidate cache when category is updated
        cache.delete('categories_list')
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Invalidate cache when category is deleted
        cache.delete('categories_list')
        super().delete(*args, **kwargs)

class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    stock = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        # Invalidate cache when product is updated
        cache.delete('products_list')
        cache.delete(f'product_{self.id}')
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Invalidate cache when product is deleted
        cache.delete('products_list')
        cache.delete(f'product_{self.id}')
        super().delete(*args, **kwargs)
    
    @property
    def in_stock(self):
        return self.stock > 0