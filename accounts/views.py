from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from accounts.models import User, Role
from accounts.serializers import UserSerializer, UserCreateUpdateSerializer
from accounts.permissions import RoleBasedHierarchyPermission

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated, RoleBasedHierarchyPermission]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['id', 'username', 'date_joined']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return UserCreateUpdateSerializer
        return UserSerializer

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return User.objects.none()
            
        if user.role == Role.SUPER_ADMIN:
            return User.objects.all()
        elif user.role == Role.HQ_ADMIN:
            # HQ Admin can see all users in their HQ except Super Admins
            return User.objects.filter(headquarters=user.headquarters).exclude(role=Role.SUPER_ADMIN)
        else:
            # Others can only see themselves
            return User.objects.filter(id=user.id)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
