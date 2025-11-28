from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Notification
from rest_framework import serializers

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['created_at']

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.none()  # For schema generation
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Skip queryset evaluation during schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Notification.objects.none()
        
        # Users can only see their own notifications
        return Notification.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
