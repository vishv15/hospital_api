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
            
        
        if request.user.role == Role.SUPER_ADMIN:
            return True
            
       
        if request.method in permissions.SAFE_METHODS:
            return True
            
        user_role = request.user.role
        
       
        model_name = None
        if hasattr(view, 'queryset') and view.queryset is not None:
            model_name = view.queryset.model.__name__
        elif hasattr(view, 'get_queryset'):
            try:
                model_name = view.get_queryset().model.__name__
            except Exception:
                pass

       
        if model_name == 'User':
          
            return user_role in [Role.SUPER_ADMIN, Role.HQ_ADMIN]

        if model_name == 'Headquarters':
            return user_role == Role.SUPER_ADMIN

   
        if model_name == 'SubHeadquarters':
            return user_role in [Role.SUPER_ADMIN, Role.HQ_ADMIN]

        
        if model_name == 'Doctor':
            return user_role in [Role.SUPER_ADMIN, Role.HQ_ADMIN, Role.HQ_STAFF, Role.SUB_HQ_STAFF]


        if model_name == 'Visit':
            return True
            
        return False

