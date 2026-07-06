from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class Review(models.Model):
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='given_reviews'
    )
    reviewed_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_reviews'
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['reviewer', 'reviewed_user']  # One review per pair
        indexes = [
            models.Index(fields=['reviewed_user']),
            models.Index(fields=['rating']),
        ]
    
    def __str__(self):
        return f"{self.reviewer.username} → {self.reviewed_user.username} ({self.rating}★)"
    
    @classmethod
    def get_average_rating(cls, user):
        """Get average rating for a user"""
        avg = cls.objects.filter(reviewed_user=user).aggregate(
            models.Avg('rating')
        )['rating__avg']
        return round(avg, 2) if avg else 0


class ProductReview(models.Model):
    """Reviews for specific scrap items"""
    from listings.models import ScrapItem
    
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='product_reviews'
    )
    scrap_item = models.ForeignKey(
        'listings.ScrapItem',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['reviewer', 'scrap_item']
    
    def __str__(self):
        return f"Review of {self.scrap_item.title} by {self.reviewer.username}"