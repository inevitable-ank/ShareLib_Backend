
# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    bio = models.TextField(blank=True, max_length=500, help_text='User biography or description')
    lender_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    borrower_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)