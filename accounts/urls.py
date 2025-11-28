from django.urls import path
from .views import RegisterView, UserProfileView, EmailLoginView, UserDetailView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('register/profile/', UserProfileView.as_view(), name='user-profile'),
    path('login/email/', EmailLoginView.as_view(), name='email-login'),
]

