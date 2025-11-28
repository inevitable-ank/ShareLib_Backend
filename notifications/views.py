from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from .models import Notification
from rest_framework import serializers
from items.serializers import ItemSerializer
from borrows.serializers import BorrowRequestSerializer


class NotificationSerializer(serializers.ModelSerializer):
    is_read = serializers.BooleanField(source='read', read_only=True)
    related_item = ItemSerializer(read_only=True)
    related_request = BorrowRequestSerializer(read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'type', 'title', 'message', 'is_read', 
            'created_at', 'related_item', 'related_request', 'metadata'
        ]
        read_only_fields = ['created_at', 'is_read']


class NotificationPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.none()  # For schema generation
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = NotificationPagination
    
    def get_queryset(self):
        # Skip queryset evaluation during schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Notification.objects.none()
        
        # Users can only see their own notifications
        queryset = Notification.objects.filter(user=self.request.user)
        
        # Filter by read status if provided
        filter_param = self.request.query_params.get('filter', 'all')
        if filter_param == 'unread':
            queryset = queryset.filter(read=False)
        elif filter_param == 'read':
            queryset = queryset.filter(read=True)
        # 'all' or any other value shows all notifications
        
        return queryset
    
    def list(self, request, *args, **kwargs):
        """Override list to include unread_count in response"""
        queryset = self.filter_queryset(self.get_queryset())
        
        # Calculate unread count for the user
        unread_count = Notification.objects.filter(
            user=request.user, 
            read=False
        ).count()
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            # Add unread_count to the response
            response.data['unread_count'] = unread_count
            return response
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': len(serializer.data),
            'unread_count': unread_count,
            'results': serializer.data
        })
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['patch'], url_path='read')
    def mark_read(self, request, pk=None):
        """Mark a notification as read"""
        notification = self.get_object()
        if notification.user != request.user:
            return Response(
                {'detail': 'You do not have permission to perform this action.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        notification.read = True
        notification.save()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], url_path='mark-all-read')
    def mark_all_read(self, request):
        """Mark all notifications as read for the current user"""
        updated_count = Notification.objects.filter(
            user=request.user,
            read=False
        ).update(read=True)
        
        return Response({
            'message': f'Successfully marked {updated_count} notification(s) as read.',
            'updated_count': updated_count
        }, status=status.HTTP_200_OK)
    
    def destroy(self, request, *args, **kwargs):
        """Delete a notification - returns 204 No Content"""
        instance = self.get_object()
        if instance.user != request.user:
            return Response(
                {'detail': 'You do not have permission to perform this action.'},
                status=status.HTTP_403_FORBIDDEN
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
