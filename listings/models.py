from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator



class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.ImageField(upload_to='category_icons/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ScrapItem(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('sold', 'Sold'),
        ('inactive', 'Inactive'),
    ]
    
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='scrap_listings'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='items'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='scrap_items/%Y/%m/%d/')
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_unit = models.CharField(
        max_length=20,
        choices=[
            ('kg', 'Kilogram'),
            ('ton', 'Ton'),
            ('piece', 'Piece'),
            ('liter', 'Liter'),
            ('meter', 'Meter'),
        ],
        default='kg'
    )
    expected_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    location = models.CharField(max_length=255)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['seller', 'status']),
            models.Index(fields=['category']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.seller.username}"
    
    def mark_as_sold(self):
        self.status = 'sold'
        self.save()
    
    def get_active_bids_count(self):
        """Get count of pending bids"""
        from bids.models import Bid
        return Bid.objects.filter(
            scrap_item=self,
            status='pending'
        ).count()