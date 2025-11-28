from django.db import models
from accounts.models import User
from items.models import Item

class BorrowRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]
    
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='borrow_requests')
    borrower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrow_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    request_date = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True)
    start_date = models.DateTimeField(null=True, blank=True)  # Requested start date
    end_date = models.DateTimeField(null=True, blank=True)  # Requested end date

class BorrowRecord(models.Model):
    STATUS_CHOICES = [
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
        ('late', 'Late'),
        ('overdue', 'Overdue'),
    ]
    
    request = models.OneToOneField(BorrowRequest, on_delete=models.CASCADE, related_name='borrow_record')
    start_date = models.DateTimeField()
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='borrowed')
    created_at = models.DateTimeField(auto_now_add=True)

class DamageReport(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('resolved', 'Resolved'),
    ]
    
    borrow_record = models.ForeignKey(BorrowRecord, on_delete=models.CASCADE, related_name='damage_reports')
    description = models.TextField()
    photo = models.ImageField(upload_to='damage_reports/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)