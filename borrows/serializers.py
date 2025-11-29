from rest_framework import serializers
from .models import BorrowRequest, BorrowRecord, DamageReport
from items.models import Item
from items.serializers import ItemSerializer
from accounts.serializers import UserSerializer

class BorrowRequestSerializer(serializers.ModelSerializer):
    item = ItemSerializer(read_only=True)
    item_id = serializers.PrimaryKeyRelatedField(
        queryset=Item.objects.all(),
        source='item',
        write_only=True
    )
    borrower = serializers.SerializerMethodField()  # Use method field to pass context
    requester = serializers.SerializerMethodField()  # Alias for borrower (frontend compatibility)
    requested_at = serializers.DateTimeField(source='request_date', read_only=True)  # Alias for request_date
    created_at = serializers.DateTimeField(source='request_date', read_only=True)  # Alias for request_date
    
    class Meta:
        model = BorrowRequest
        fields = '__all__'
        read_only_fields = ['request_date', 'requester', 'requested_at', 'created_at']
    
    def get_borrower(self, obj):
        """Return borrower with proper context for rating display."""
        # Pass context to UserSerializer to show borrower_rating when viewing as lender
        serializer = UserSerializer(obj.borrower, context={'rating_context': 'borrower'})
        return serializer.data
    
    def get_requester(self, obj):
        """Return borrower as 'requester' for frontend compatibility."""
        # Same as borrower, just an alias
        return self.get_borrower(obj)

class BorrowRecordSerializer(serializers.ModelSerializer):
    request = BorrowRequestSerializer(read_only=True)
    
    class Meta:
        model = BorrowRecord
        fields = '__all__'