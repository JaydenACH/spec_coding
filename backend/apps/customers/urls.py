"""
URL patterns for customer management.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet

router = DefaultRouter()
router.register(r'', CustomerViewSet, basename='customer')

app_name = 'customers'

urlpatterns = [
    path('', include(router.urls)),
] 