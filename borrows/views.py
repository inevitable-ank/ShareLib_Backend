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
        queryset = BorrowRequest.objects.all()
        
        # Filter by query parameters
        lender = self.request.query_params.get('lender', None)
        owner = self.request.query_params.get('owner', None)
        borrower = self.request.query_params.get('borrower', None)
        
        # If specific filters are requested, apply them
        if lender == 'me' or owner == 'me':
            # Return only requests for items the user owns (as lender)
            queryset = queryset.filter(item__owner=user)
        elif borrower == 'me':
            # Return only requests where the user is the borrower
            queryset = queryset.filter(borrower=user)
        else:
            # Default: Users can see their own requests and requests for items they own
            queryset = queryset.filter(
                borrower=user
            ) | queryset.filter(
                item__owner=user
            )
        
        return queryset
    
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
        borrow_request = self.get_object()
        old_status = borrow_request.status
        
        # Only allow item owner to approve/reject requests
        if borrow_request.item.owner != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only the item owner can approve or reject requests.")
        
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
        queryset = BorrowRecord.objects.all()
        
        # Filter by query parameters
        owner = self.request.query_params.get('owner', None)
        borrower = self.request.query_params.get('borrower', None)
        
        # If specific filters are requested, apply them
        if owner:
            # Filter by owner ID (can be 'me' or specific ID)
            if owner == 'me':
                queryset = queryset.filter(request__item__owner=user)
            else:
                try:
                    owner_id = int(owner)
                    queryset = queryset.filter(request__item__owner_id=owner_id)
                except (ValueError, TypeError):
                    pass  # Invalid owner ID, return empty queryset
        elif borrower:
            # Filter by borrower ID (can be 'me' or specific ID)
            if borrower == 'me':
                queryset = queryset.filter(request__borrower=user)
            else:
                try:
                    borrower_id = int(borrower)
                    queryset = queryset.filter(request__borrower_id=borrower_id)
                except (ValueError, TypeError):
                    pass  # Invalid borrower ID, return empty queryset
        else:
            # Default: Users can see records where they are borrower or owner
            queryset = queryset.filter(
                request__borrower=user
            ) | queryset.filter(
                request__item__owner=user
            )
        
        return queryset
    
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
