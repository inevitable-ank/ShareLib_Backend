from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Rating
from items.models import Item
from rest_framework import serializers

class RatingSerializer(serializers.ModelSerializer):
    from_user = serializers.StringRelatedField(read_only=True)
    to_user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Rating
        fields = '__all__'
        read_only_fields = ['from_user', 'created_at']

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
        serializer.save(from_user=self.request.user)
    
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
