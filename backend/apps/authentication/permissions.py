"""
Custom permission classes for role-based access control.
"""

from rest_framework import permissions


class IsSystemAdmin(permissions.BasePermission):
    """
    Permission class for system administrators only.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_system_admin
        )


class IsManagerOrSystemAdmin(permissions.BasePermission):
    """
    Permission class for managers and system administrators.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            (request.user.is_manager or request.user.is_system_admin)
        )


class IsOwnerOrSystemAdmin(permissions.BasePermission):
    """
    Permission class that allows access to owners or system administrators.
    """
    
    def has_object_permission(self, request, view, obj):
        # System admins can access everything
        if request.user.is_system_admin:
            return True
        
        # Check if object has a user field (owner)
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # Check if object is the user themselves
        if hasattr(obj, 'id') and hasattr(request.user, 'id'):
            return obj.id == request.user.id
        
        return False


class IsAssignedUserOrManager(permissions.BasePermission):
    """
    Permission class for assigned users, managers, and system administrators.
    """
    
    def has_object_permission(self, request, view, obj):
        # Managers and system admins can access everything
        if request.user.is_manager or request.user.is_system_admin:
            return True
        
        # Check if user is assigned to the object
        if hasattr(obj, 'assigned_user'):
            return obj.assigned_user == request.user
        
        # Check if object belongs to user's assigned customers
        if hasattr(obj, 'customer') and hasattr(obj.customer, 'assigned_user'):
            return obj.customer.assigned_user == request.user
        
        return False


class CanViewCustomers(permissions.BasePermission):
    """
    Permission class for viewing customers based on role.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.can_view_all_customers
        )


class CanAssignCustomers(permissions.BasePermission):
    """
    Permission class for assigning customers.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.can_assign_customers
        )


class CanManageUsers(permissions.BasePermission):
    """
    Permission class for user management.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.can_manage_users
        ) 