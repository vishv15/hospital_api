"""
URL configuration for hospital_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from accounts.views import UserViewSet
from core.views import (
    HeadquartersViewSet,
    SubHeadquartersViewSet,
    DoctorViewSet,
    VisitViewSet,
    DashboardAPIView,
)

# Register ViewSets with the DefaultRouter
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'headquarters', HeadquartersViewSet, basename='headquarters')
router.register(r'sub-headquarters', SubHeadquartersViewSet, basename='subheadquarters')
router.register(r'doctors', DoctorViewSet, basename='doctor')
router.register(r'visits', VisitViewSet, basename='visit')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # JWT Authentication endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Dashboard endpoint
    path('api/dashboard/', DashboardAPIView.as_view(), name='dashboard'),
    
    # CRUD API endpoints
    path('api/', include(router.urls)),
]

