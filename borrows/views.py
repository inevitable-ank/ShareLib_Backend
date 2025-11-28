from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import BorrowRequest, BorrowRecord
from .serializers import BorrowRequestSerializer, BorrowRecordSerializer

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
        serializer.save(borrower=self.request.user)

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
