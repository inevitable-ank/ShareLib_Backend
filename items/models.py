# Create your models here.
from django.db import models
from accounts.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Item(models.Model):
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('good', 'Good'),
        ('used', 'Used'),
        ('damaged', 'Damaged'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('requested', 'Requested'),
        ('borrowed', 'Borrowed'),
        ('under_review', 'Under Review'),
    ]
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_items')
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='good')
    photos = models.ImageField(upload_to='items/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title