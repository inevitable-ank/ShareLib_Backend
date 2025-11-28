
# Create your models here.
from django.db import models
from accounts.models import User
from items.models import Item

class Rating(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings_given')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings_received')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='ratings')
    stars = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['from_user', 'to_user', 'item']