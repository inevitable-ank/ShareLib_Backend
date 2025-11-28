from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BorrowRequestViewSet, BorrowRecordViewSet

router = DefaultRouter()
router.register(r'requests', BorrowRequestViewSet, basename='borrow-request')
router.register(r'records', BorrowRecordViewSet, basename='borrow-record')

urlpatterns = [
    path('', include(router.urls)),
]

