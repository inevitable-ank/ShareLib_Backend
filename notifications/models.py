
# Create your models here.
from django.db import models
from accounts.models import User

class Notification(models.Model):
    TYPE_CHOICES = [
        ('request', 'Borrow Request'),
        ('approved', 'Request Approved'),
        ('rejected', 'Request Rejected'),
        ('due_soon', 'Due Soon'),
        ('overdue', 'Overdue'),
        ('returned', 'Item Returned'),
        ('rating', 'Rating Received'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    message = models.TextField()
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
