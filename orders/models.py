from django.db import models
from django.contrib.auth import get_user_model
from listings.models import ScrapItem

User = get_user_model()

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    buyer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='buyer_orders'
    )
    seller = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='seller_orders'
    )
    scrap_item = models.ForeignKey(
        ScrapItem,
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders'
    )
    final_price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='pending'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['buyer', 'status']),
            models.Index(fields=['seller', 'status']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Order {self.id} - {self.buyer.username} → {self.seller.username}"
    
    def mark_completed(self):
        from django.utils import timezone
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
    
    def cancel_order(self):
        if self.status in ['pending', 'accepted']:
            self.status = 'cancelled'
            self.save()
            # Reactivate listing
            if self.scrap_item:
                self.scrap_item.status = 'active'
                self.scrap_item.save()