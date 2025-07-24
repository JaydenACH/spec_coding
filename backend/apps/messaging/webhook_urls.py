"""
URL patterns for Respond.IO webhook endpoints.
"""

from django.urls import path
from .webhook_views import RespondIOMessageWebhook, RespondIOAssignmentWebhook

urlpatterns = [
    path('message/', RespondIOMessageWebhook.as_view(), name='respondio_message_webhook'),
    path('assignment/', RespondIOAssignmentWebhook.as_view(), name='respondio_assignment_webhook'),
] 