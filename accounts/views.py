from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db.models import Avg
from .models import User
from .serializers import UserSerializer, RegisterSerializer, EmailLoginSerializer
from items.models import Item
from borrows.models import BorrowRecord
from ratings.models import Rating

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'user': UserSerializer(user).data,
            'message': 'User created successfully'
        }, status=status.HTTP_201_CREATED)

class EmailLoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = EmailLoginSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'detail': 'No active account found with the given credentials.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        user = authenticate(username=user.username, password=password)
        
        if user is None:
            return Response(
                {'detail': 'No active account found with the given credentials.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }, status=status.HTTP_200_OK)

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user

class UserDetailView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]  # Public user profiles
    queryset = User.objects.all()
    lookup_field = 'id'
    lookup_url_kwarg = 'id'

class UserStatsView(generics.RetrieveAPIView):
    """
    Get user statistics including items lent, items borrowed, active loans, and ratings.
    GET /api/users/me/stats/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        user = request.user
        
        # Calculate items lent (total items owned by user)
        items_lent = Item.objects.filter(owner=user).count()
        
        # Calculate items borrowed (count of borrow records where user is borrower)
        # This includes both active and completed borrows
        items_borrowed = BorrowRecord.objects.filter(
            request__borrower=user,
            status__in=['borrowed', 'returned']
        ).count()
        
        # Calculate active loans (currently borrowed items)
        active_loans = BorrowRecord.objects.filter(
            request__borrower=user,
            status='borrowed'
        ).count()
        
        # Calculate average lender rating
        # Lender rating: ratings where the user (to_user) owns the item
        lender_ratings_avg = Rating.objects.filter(
            to_user=user,
            item__owner=user
        ).aggregate(avg_rating=Avg('stars'))['avg_rating']
        
        average_lender_rating = f"{lender_ratings_avg:.2f}" if lender_ratings_avg else "0.00"
        
        # Calculate average borrower rating
        # Borrower rating: ratings where the user (to_user) borrowed the item (doesn't own it)
        borrower_ratings_avg = Rating.objects.filter(
            to_user=user
        ).exclude(item__owner=user).aggregate(avg_rating=Avg('stars'))['avg_rating']
        
        average_borrower_rating = f"{borrower_ratings_avg:.2f}" if borrower_ratings_avg else "0.00"
        
        return Response({
            'items_lent': items_lent,
            'items_borrowed': items_borrowed,
            'active_loans': active_loans,
            'average_lender_rating': average_lender_rating,
            'average_borrower_rating': average_borrower_rating
        })