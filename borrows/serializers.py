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
    borrower = UserSerializer(read_only=True)
    
    class Meta:
        model = BorrowRequest
        fields = '__all__'
        read_only_fields = ['borrower', 'request_date']

class BorrowRecordSerializer(serializers.ModelSerializer):
    request = BorrowRequestSerializer(read_only=True)
    
    class Meta:
        model = BorrowRecord
        fields = '__all__'