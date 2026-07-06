from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import URLValidator
import os

class User(AbstractUser):
    ROLE_CHOICES = [
        ('seller', 'Seller'),
        ('buyer', 'Buyer'),
        ('admin', 'Admin'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='buyer')
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_image = models.ImageField(
        upload_to='profile_images/%Y/%m/%d/',
        blank=True,
        null=True
    )
    bio = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['is_verified']),
        ]
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def get_seller_rating(self):
        """Calculate average rating as seller"""
        from reviews.models import Review
        avg = Review.objects.filter(reviewed_user=self, reviewer_role='buyer').aggregate(
            models.Avg('rating')
        )['rating__avg']
        return round(avg, 2) if avg else 0