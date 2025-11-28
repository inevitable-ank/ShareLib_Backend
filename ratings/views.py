from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Rating
from rest_framework import serializers

class RatingSerializer(serializers.ModelSerializer):
    from_user = serializers.StringRelatedField(read_only=True)
    to_user = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = Rating
        fields = '__all__'
        read_only_fields = ['from_user', 'created_at']

class RatingViewSet(viewsets.ModelViewSet):
    serializer_class = RatingSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Users can see ratings they gave and ratings they received
        user = self.request.user
        return Rating.objects.filter(
            from_user=user
        ) | Rating.objects.filter(
            to_user=user
        )
    
    def perform_create(self, serializer):
        serializer.save(from_user=self.request.user)
