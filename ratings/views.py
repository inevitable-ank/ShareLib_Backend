from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Rating
from items.models import Item
from rest_framework import serializers
from notifications.utils import create_notification

class RatingSerializer(serializers.ModelSerializer):
    from_user = serializers.StringRelatedField(read_only=True)
    to_user = serializers.StringRelatedField(read_only=True)
    rating_type = serializers.SerializerMethodField()
    
    class Meta:
        model = Rating
        fields = '__all__'
        read_only_fields = ['from_user', 'created_at', 'rating_type']
    
    def get_rating_type(self, obj):
        """
        Derive rating_type from item ownership.
        If to_user owns the item, it's a lender rating.
        Otherwise, it's a borrower rating.
        """
        if obj.item.owner == obj.to_user:
            return 'lender'
        return 'borrower'

class RatingViewSet(viewsets.ModelViewSet):
    queryset = Rating.objects.none()  # For schema generation
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Skip queryset evaluation during schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Rating.objects.none()
        
        # Users can see ratings they gave and ratings they received
        user = self.request.user
        return Rating.objects.filter(
            from_user=user
        ) | Rating.objects.filter(
            to_user=user
        )
    
    def perform_create(self, serializer):
        rating = serializer.save(from_user=self.request.user)
        
        # Create notification for the user who received the rating
        if rating.to_user != self.request.user:  # Don't notify if rating yourself
            create_notification(
                user=rating.to_user,
                notification_type='rating',
                title='New Review Received',
                message=f"{self.request.user.get_full_name() or self.request.user.email} left you a {rating.stars}-star review for {rating.item.title}",
                related_item=rating.item,
                metadata={
                    'from_user_name': self.request.user.get_full_name() or self.request.user.email,
                    'item_title': rating.item.title,
                    'stars': rating.stars,
                    'rating_message': rating.message
                }
            )
    
    @action(detail=False, methods=['get'], url_path='item/(?P<item_id>[^/.]+)', permission_classes=[AllowAny])
    def by_item(self, request, item_id=None):
        """
        Get all ratings for a specific item
        GET /api/ratings/item/{item_id}/
        """
        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            return Response(
                {'detail': 'Item not found.'},
                status=404
            )
        
        ratings = Rating.objects.filter(item=item).order_by('-created_at')
        serializer = self.get_serializer(ratings, many=True)
        return Response(serializer.data)
