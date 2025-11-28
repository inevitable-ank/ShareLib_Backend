"""
Utility functions for creating notifications
"""
from .models import Notification


def create_notification(user, notification_type, title, message, related_item=None, related_request=None, metadata=None):
    """
    Helper function to create a notification
    
    Args:
        user: User instance to receive the notification
        notification_type: Type of notification (e.g., 'request', 'approved', 'returned', 'rating', 'reminder', 'message')
        title: Notification title
        message: Notification message
        related_item: Optional Item instance
        related_request: Optional BorrowRequest instance
        metadata: Optional dict with additional data
    
    Returns:
        Created Notification instance
    """
    notification = Notification.objects.create(
        user=user,
        type=notification_type,
        title=title,
        message=message,
        related_item=related_item,
        related_request=related_request,
        metadata=metadata or {}
    )
    return notification

