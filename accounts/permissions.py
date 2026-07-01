from rest_framework import permissions
from accounts.models import Role

class IsSuperAdmin(permissions.BasePermission):
    """
    Allows access only to Super Admins.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == Role.SUPER_ADMIN)


class IsHQAdmin(permissions.BasePermission):
    """
    Allows access only to HQ Admins.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == Role.HQ_ADMIN)


class IsHQStaff(permissions.BasePermission):
    """
    Allows access only to HQ Staff.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == Role.HQ_STAFF)


class IsSubHQStaff(permissions.BasePermission):
    """
    Allows access only to Sub HQ Staff.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == Role.SUB_HQ_STAFF)


class IsMR(permissions.BasePermission):
    """
    Allows access only to Medical Representatives (MRs).
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == Role.MR)


class IsSuperAdminOrReadOnly(permissions.BasePermission):
    """
    Allows full access to Super Admins, and read-only access to others.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.user.role == Role.SUPER_ADMIN:
            return True
        return request.method in permissions.SAFE_METHODS


class RoleBasedHierarchyPermission(permissions.BasePermission):

    """
    Custom permission class to enforce the role-based hierarchy dynamically.
    Instead of hardcoding in every API, views can use this to check general access,
    and we will also filter the querysets at the view level (get_queryset) for safety.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
            
        # Super admin has bypass access
        if request.user.role == Role.SUPER_ADMIN:
            return True
            
        # Safe methods (GET, HEAD, OPTIONS) are generally allowed for authenticated users,
        # but queryset filtering will restrict what they can actually see.
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Unsafe methods require specific write permissions
        user_role = request.user.role
        
        # HQ Admin can perform writes (POST, PUT, PATCH, DELETE)
        if user_role == Role.HQ_ADMIN:
            # Can manage SubHQs, Users (except other HQ Admins or Super Admins), Doctors, and Visits.
            return True
            
        # HQ Staff can perform writes on Doctors and Visits
        if user_role == Role.HQ_STAFF:
            # Views will enforce that HQ Staff can only manage their own HQ's doctors/visits
            return True
            
        # Sub HQ Staff can perform writes on Doctors and Visits
        if user_role == Role.SUB_HQ_STAFF:
            # Views will enforce they only manage their assigned Sub HQ's doctors/visits
            return True
            
        # MR can perform writes on Visits (submitting daily reports)
        if user_role == Role.MR:
            # Views will restrict them to creating visits for themselves on their assigned doctors
            return True
            
        return False
