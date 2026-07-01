from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q

from core.models import Headquarters, SubHeadquarters, Doctor, Visit, VisitStatus
from core.serializers import HeadquartersSerializer, SubHeadquartersSerializer, DoctorSerializer, VisitSerializer
from core.filters import VisitFilter
from accounts.models import User, Role
from accounts.permissions import RoleBasedHierarchyPermission, IsSuperAdminOrReadOnly

class HeadquartersViewSet(viewsets.ModelViewSet):
    serializer_class = HeadquartersSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdminOrReadOnly]
    search_fields = ['name', 'location']
    ordering_fields = ['id', 'name']

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Headquarters.objects.none()
            
        if user.role == Role.SUPER_ADMIN:
            return Headquarters.objects.all()
        elif user.headquarters:
            return Headquarters.objects.filter(id=user.headquarters.id)
        return Headquarters.objects.none()


class SubHeadquartersViewSet(viewsets.ModelViewSet):
    serializer_class = SubHeadquartersSerializer
    permission_classes = [permissions.IsAuthenticated, RoleBasedHierarchyPermission]
    search_fields = ['name', 'location']
    ordering_fields = ['id', 'name']

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return SubHeadquarters.objects.none()
            
        if user.role == Role.SUPER_ADMIN:
            return SubHeadquarters.objects.all()
        elif user.role in [Role.HQ_ADMIN, Role.HQ_STAFF]:
            if user.headquarters:
                return SubHeadquarters.objects.filter(headquarters=user.headquarters)
            return SubHeadquarters.objects.none()
        elif user.role in [Role.SUB_HQ_STAFF, Role.MR]:
            if user.sub_headquarters:
                return SubHeadquarters.objects.filter(id=user.sub_headquarters.id)
            elif user.headquarters: 
                return SubHeadquarters.objects.filter(headquarters=user.headquarters)
            return SubHeadquarters.objects.none()
        return SubHeadquarters.objects.none()


class DoctorViewSet(viewsets.ModelViewSet):
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated, RoleBasedHierarchyPermission]
    search_fields = ['name', 'specialization']
    ordering_fields = ['id', 'name', 'created_at']

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Doctor.objects.none()
            
        if user.role == Role.SUPER_ADMIN:
            return Doctor.objects.all()
        elif user.role in [Role.HQ_ADMIN, Role.HQ_STAFF]:
            
            return Doctor.objects.filter(
                Q(headquarters=user.headquarters) | 
                Q(sub_headquarters__headquarters=user.headquarters)
            ).distinct()
        elif user.role == Role.SUB_HQ_STAFF:
            if user.sub_headquarters:
                return Doctor.objects.filter(sub_headquarters=user.sub_headquarters)
            return Doctor.objects.none()
        elif user.role == Role.MR:
            
            return Doctor.objects.filter(assigned_mrs=user)
        return Doctor.objects.none()


class VisitViewSet(viewsets.ModelViewSet):
    serializer_class = VisitSerializer
    permission_classes = [permissions.IsAuthenticated, RoleBasedHierarchyPermission]
    filterset_class = VisitFilter
    search_fields = ['doctor__name', 'mr__username', 'notes']
    ordering_fields = ['id', 'date', 'created_at']

    def get_queryset(self):
        user = self.request.user
        if not user or not user.is_authenticated:
            return Visit.objects.none()
            
        if user.role == Role.SUPER_ADMIN:
            return Visit.objects.all()
        elif user.role in [Role.HQ_ADMIN, Role.HQ_STAFF]:
            return Visit.objects.filter(
                Q(mr__headquarters=user.headquarters) | Q(doctor__headquarters=user.headquarters)
            ).distinct()
        elif user.role == Role.SUB_HQ_STAFF:
            if user.sub_headquarters:
                return Visit.objects.filter(
                    Q(mr__sub_headquarters=user.sub_headquarters) | Q(doctor__sub_headquarters=user.sub_headquarters)
                ).distinct()
            return Visit.objects.none()
        elif user.role == Role.MR:
            return Visit.objects.filter(mr=user)
        return Visit.objects.none()


class DashboardAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        today = timezone.localtime(timezone.now()).date()

       
        if user.role == Role.SUPER_ADMIN:
            total_hqs = Headquarters.objects.count()
            total_sub_hqs = SubHeadquarters.objects.count()
            total_doctors = Doctor.objects.count()
            total_mrs = User.objects.filter(role=Role.MR).count()
            todays_visits = Visit.objects.filter(date=today).count()
            completed_visits = Visit.objects.filter(status=VisitStatus.COMPLETED).count()
            pending_visits = Visit.objects.filter(status=VisitStatus.PENDING).count()

        elif user.role in [Role.HQ_ADMIN, Role.HQ_STAFF]:
            hq = user.headquarters
            if hq:
                total_hqs = 1
                total_sub_hqs = SubHeadquarters.objects.filter(headquarters=hq).count()
                total_doctors = Doctor.objects.filter(
                    Q(headquarters=hq) | Q(sub_headquarters__headquarters=hq)
                ).distinct().count()
                total_mrs = User.objects.filter(role=Role.MR, headquarters=hq).count()
                todays_visits = Visit.objects.filter(date=today, mr__headquarters=hq).count()
                completed_visits = Visit.objects.filter(status=VisitStatus.COMPLETED, mr__headquarters=hq).count()
                pending_visits = Visit.objects.filter(status=VisitStatus.PENDING, mr__headquarters=hq).count()
            else:
                total_hqs = total_sub_hqs = total_doctors = total_mrs = todays_visits = completed_visits = pending_visits = 0

        elif user.role == Role.SUB_HQ_STAFF:
            sub_hq = user.sub_headquarters
            if sub_hq:
                total_hqs = 1
                total_sub_hqs = 1
                total_doctors = Doctor.objects.filter(sub_headquarters=sub_hq).count()
                total_mrs = User.objects.filter(role=Role.MR, sub_headquarters=sub_hq).count()
                todays_visits = Visit.objects.filter(date=today, mr__sub_headquarters=sub_hq).count()
                completed_visits = Visit.objects.filter(status=VisitStatus.COMPLETED, mr__sub_headquarters=sub_hq).count()
                pending_visits = Visit.objects.filter(status=VisitStatus.PENDING, mr__sub_headquarters=sub_hq).count()
            else:
                total_hqs = total_sub_hqs = total_doctors = total_mrs = todays_visits = completed_visits = pending_visits = 0

        elif user.role == Role.MR:
            total_hqs = 1 if user.headquarters else 0
            total_sub_hqs = 1 if user.sub_headquarters else 0
            total_doctors = Doctor.objects.filter(assigned_mrs=user).count()
            total_mrs = 1
            todays_visits = Visit.objects.filter(date=today, mr=user).count()
            completed_visits = Visit.objects.filter(status=VisitStatus.COMPLETED, mr=user).count()
            pending_visits = Visit.objects.filter(status=VisitStatus.PENDING, mr=user).count()
        else:
            total_hqs = total_sub_hqs = total_doctors = total_mrs = todays_visits = completed_visits = pending_visits = 0

        return Response({
            "total_hqs": total_hqs,
            "total_sub_hqs": total_sub_hqs,
            "total_doctors": total_doctors,
            "total_mrs": total_mrs,
            "todays_visits": todays_visits,
            "completed_visits": completed_visits,
            "pending_visits": pending_visits,
        })
