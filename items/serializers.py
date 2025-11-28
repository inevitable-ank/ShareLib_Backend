from rest_framework import serializers
from .models import Item, Category
from accounts.serializers import UserSerializer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), 
        source='category', 
        write_only=True
    )
    photos = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()  # Alias for photos (frontend compatibility)
    
    class Meta:
        model = Item
        fields = '__all__'
        read_only_fields = ['owner', 'created_at', 'updated_at']
    
    def get_photos(self, obj):
        """
        Return absolute URL(s) for the photos field.
        Since the model has a single ImageField, we return it as an array
        to match frontend expectations. If no photo, returns empty array.
        """
        return self._get_image_urls(obj)
    
    def get_images(self, obj):
        """
        Alias for photos field - returns the same data.
        Frontend may use either 'photos' or 'images' field name.
        """
        return self._get_image_urls(obj)
    
    def _get_image_urls(self, obj):
        """Helper method to get image URLs as array."""
        if obj.photos:
            request = self.context.get('request')
            if request:
                # Return absolute URL in array format
                return [request.build_absolute_uri(obj.photos.url)]
            else:
                # Fallback to relative URL if no request context
                return [obj.photos.url] if obj.photos else []
        return []