from django.db import models
from django.contrib.auth import get_user_model
from listings.models import ScrapItem
from django.core.validators import MinValueValidator
from django.utils import timezone

User = get_user_model()

class Bid(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    buyer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='submitted_bids'
    )
    scrap_item = models.ForeignKey(
        ScrapItem,
        on_delete=models.CASCADE,
        related_name='bids'
    )
    offered_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['buyer', 'scrap_item']  # One bid per buyer per item
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['buyer']),
            models.Index(fields=['scrap_item']),
        ]
    
    def __str__(self):
        return f"Bid {self.id} - {self.buyer.username} on {self.scrap_item.title}"
    
    def accept(self):
        """Accept bid and create order"""
        self.status = 'accepted'
        self.responded_at = timezone.now()
        self.save()
        
        # Auto-create order
        from orders.models import Order
        Order.objects.create(
            buyer=self.buyer,
            seller=self.scrap_item.seller,
            scrap_item=self.scrap_item,
            final_price=self.offered_price,
            status='accepted'
        )
        
        # Reject other bids for same item
        Bid.objects.filter(
            scrap_item=self.scrap_item,
            status='pending'
        ).exclude(id=self.id).update(status='rejected')
        
        # Mark item as sold
        self.scrap_item.mark_as_sold()
    
    def reject(self):
        self.status = 'rejected'
        self.responded_at = timezone.now()
        self.save()
    
    def cancel(self):
        if self.status == 'pending':
            self.status = 'cancelled'
            self.save()