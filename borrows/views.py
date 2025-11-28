from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import BorrowRequest, BorrowRecord
from .serializers import BorrowRequestSerializer, BorrowRecordSerializer
from notifications.utils import create_notification


class BorrowRequestViewSet(viewsets.ModelViewSet):
    queryset = BorrowRequest.objects.none()  # For schema generation
    serializer_class = BorrowRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Skip queryset evaluation during schema generation
        if getattr(self, 'swagger_fake_view', False):
            return BorrowRequest.objects.none()
        
        user = self.request.user
        # Users can see their own requests and requests for items they own
        return BorrowRequest.objects.filter(
            borrower=user
        ) | BorrowRequest.objects.filter(
            item__owner=user
        )
    
    def perform_create(self, serializer):
        borrow_request = serializer.save(borrower=self.request.user)
        
        # Create notification for item owner when a new request is created
        item_owner = borrow_request.item.owner
        if item_owner != self.request.user:  # Don't notify if user is requesting their own item
            create_notification(
                user=item_owner,
                notification_type='request',
                title='New Borrow Request',
                message=f"{self.request.user.get_full_name() or self.request.user.email} wants to borrow your {borrow_request.item.title}",
                related_item=borrow_request.item,
                related_request=borrow_request,
                metadata={
                    'borrower_name': self.request.user.get_full_name() or self.request.user.email,
                    'item_title': borrow_request.item.title
                }
            )
    
    def perform_update(self, serializer):
        old_status = self.get_object().status
        borrow_request = serializer.save()
        new_status = borrow_request.status
        
        # Create notification when request is approved
        if old_status != 'approved' and new_status == 'approved':
            create_notification(
                user=borrow_request.borrower,
                notification_type='approved',
                title='Request Approved',
                message=f"Your request to borrow {borrow_request.item.title} has been approved",
                related_item=borrow_request.item,
                related_request=borrow_request,
                metadata={
                    'item_title': borrow_request.item.title,
                    'item_owner': borrow_request.item.owner.get_full_name() or borrow_request.item.owner.email
                }
            )
        
        # Optional: Create notification when request is rejected
        if old_status != 'rejected' and new_status == 'rejected':
            create_notification(
                user=borrow_request.borrower,
                notification_type='rejected',
                title='Request Rejected',
                message=f"Your request to borrow {borrow_request.item.title} has been rejected",
                related_item=borrow_request.item,
                related_request=borrow_request,
                metadata={
                    'item_title': borrow_request.item.title
                }
            )


class BorrowRecordViewSet(viewsets.ModelViewSet):
    queryset = BorrowRecord.objects.none()  # For schema generation
    serializer_class = BorrowRecordSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Skip queryset evaluation during schema generation
        if getattr(self, 'swagger_fake_view', False):
            return BorrowRecord.objects.none()
        
        user = self.request.user
        # Users can see records where they are borrower or owner
        return BorrowRecord.objects.filter(
            request__borrower=user
        ) | BorrowRecord.objects.filter(
            request__item__owner=user
        )
    
    def perform_update(self, serializer):
        old_status = self.get_object().status
        borrow_record = serializer.save()
        new_status = borrow_record.status
        
        # Create notification when item is returned
        if old_status != 'returned' and new_status == 'returned':
            item_owner = borrow_record.request.item.owner
            create_notification(
                user=item_owner,
                notification_type='returned',
                title='Item Returned',
                message=f"{borrow_record.request.borrower.get_full_name() or borrow_record.request.borrower.email} has returned your {borrow_record.request.item.title}",
                related_item=borrow_record.request.item,
                related_request=borrow_record.request,
                metadata={
                    'borrower_name': borrow_record.request.borrower.get_full_name() or borrow_record.request.borrower.email,
                    'item_title': borrow_record.request.item.title,
                    'return_date': borrow_record.return_date.isoformat() if borrow_record.return_date else None
                }
            )
