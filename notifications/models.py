
# Create your models here.
from django.db import models
from accounts.models import User

class Notification(models.Model):
    TYPE_CHOICES = [
        ('request', 'Borrow Request'),
        ('approved', 'Request Approved'),
        ('rejected', 'Request Rejected'),
        ('reminder', 'Return Reminder'),
        ('overdue', 'Overdue'),
        ('returned', 'Item Returned'),
        ('rating', 'Rating Received'),
        ('message', 'New Message'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255, default='')
    message = models.TextField()
    read = models.BooleanField(default=False)
    related_item = models.ForeignKey(
        'items.Item', 
        on_delete=models.CASCADE, 
        related_name='notifications',
        null=True, 
        blank=True
    )
    related_request = models.ForeignKey(
        'borrows.BorrowRequest', 
        on_delete=models.CASCADE, 
        related_name='notifications',
        null=True, 
        blank=True
    )
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
