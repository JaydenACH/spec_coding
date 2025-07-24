"""
Customer management and assignment API endpoints.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import Customer
from .serializers import CustomerSerializer, CustomerAssignmentSerializer, AssignmentHistorySerializer
from apps.authentication.permissions import IsSystemAdmin, IsManagerOrSystemAdmin
from django.utils.translation import gettext_lazy as _

class CustomerViewSet(viewsets.ModelViewSet):
    """
    API endpoints for customer management and assignment.
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_system_admin or user.is_manager:
            return Customer.objects.all()
        else:
            return Customer.objects.filter(assigned_user=user)

    @extend_schema(
        summary="Assign customer",
        description="Assign a customer to a user (Manager/System Admin only)."
    )
    @action(detail=True, methods=['post'], permission_classes=[IsManagerOrSystemAdmin])
    def assign(self, request, pk=None):
        customer = self.get_object()
        serializer = CustomerAssignmentSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        assigned_user = serializer.validated_data['assigned_user']
        customer.assign_to_user(assigned_user, assigned_by=request.user)
        return Response({'message': _('Customer assigned successfully')}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Unassign customer",
        description="Unassign a customer (Manager/System Admin only)."
    )
    @action(detail=True, methods=['post'], permission_classes=[IsManagerOrSystemAdmin])
    def unassign(self, request, pk=None):
        customer = self.get_object()
        customer.unassign(unassigned_by=request.user)
        return Response({'message': _('Customer unassigned successfully')}, status=status.HTTP_200_OK)

    @extend_schema(
        summary="Get assignment history",
        description="Retrieve assignment history for a customer."
    )
    @action(detail=True, methods=['get'])
    def assignment_history(self, request, pk=None):
        customer = self.get_object()
        serializer = AssignmentHistorySerializer(customer.assignment_history, many=True)
        return Response(serializer.data) 