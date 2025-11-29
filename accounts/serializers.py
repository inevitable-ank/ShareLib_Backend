from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name',
                  'avatar', 'location', 'bio', 'lender_rating', 'borrower_rating', 'rating', 'date_joined']
        read_only_fields = ['lender_rating', 'borrower_rating', 'date_joined', 'full_name', 'rating']
    
    def get_full_name(self, obj):
        """Return full name or fallback to username if name is not available."""
        full_name = obj.get_full_name()
        return full_name if full_name else obj.username
    
    def get_rating(self, obj):
        """
        Return appropriate rating based on context.
        When viewing as lender (owner), show borrower_rating.
        When viewing as borrower, show lender_rating.
        Defaults to borrower_rating if context is unclear.
        """
        # Check if we're in a borrow request context (viewing as lender)
        # The context will be set by BorrowRequestSerializer
        context = self.context.get('rating_context', 'borrower')
        if context == 'borrower':
            # When viewing borrower's profile, show their borrower_rating
            return float(obj.borrower_rating) if obj.borrower_rating else 0.0
        else:
            # When viewing lender's profile, show their lender_rating
            return float(obj.lender_rating) if obj.lender_rating else 0.0

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, label='Confirm Password')
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'first_name', 'last_name', 'location']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class EmailLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
