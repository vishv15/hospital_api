from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from accounts.models import Role
from core.models import Headquarters, SubHeadquarters, Doctor, Visit, VisitStatus
import datetime

User = get_user_model()

class HospitalAPITests(APITestCase):
    def setUp(self):
        # Create HQs
        self.hq1 = Headquarters.objects.create(name="HQ One", location="Location One")
        self.hq2 = Headquarters.objects.create(name="HQ Two", location="Location Two")

        # Create SubHQs
        self.sub_hq1 = SubHeadquarters.objects.create(name="SubHQ One", headquarters=self.hq1, location="Sub Loc One")
        self.sub_hq2 = SubHeadquarters.objects.create(name="SubHQ Two", headquarters=self.hq2, location="Sub Loc Two")

        # Create Users
        self.super_admin = User.objects.create_superuser(
            username="super", password="password", role=Role.SUPER_ADMIN
        )
        self.hq_admin = User.objects.create_user(
            username="hq_admin", password="password", role=Role.HQ_ADMIN, headquarters=self.hq1
        )
        self.hq_staff = User.objects.create_user(
            username="hq_staff", password="password", role=Role.HQ_STAFF, headquarters=self.hq1
        )
        self.sub_staff = User.objects.create_user(
            username="sub_staff", password="password", role=Role.SUB_HQ_STAFF, headquarters=self.hq1, sub_headquarters=self.sub_hq1
        )
        self.mr = User.objects.create_user(
            username="mr_user", password="password", role=Role.MR, headquarters=self.hq1, sub_headquarters=self.sub_hq1
        )

        # Create Doctor
        self.doctor = Doctor.objects.create(
            name="A", specialization="Cardio", headquarters=self.hq1, sub_headquarters=self.sub_hq1
        )
        self.doctor.assigned_mrs.add(self.mr)

        # Create Visit
        self.visit = Visit.objects.create(
            mr=self.mr, doctor=self.doctor, date=datetime.date.today(), status=VisitStatus.PENDING, notes="Test"
        )

    def get_jwt_token(self, username, password):
        url = reverse('token_obtain_pair')
        response = self.client.post(url, {'username': username, 'password': password}, format='json')
        return response.data.get('access')

    def test_jwt_authentication(self):
        # Obtain token
        token = self.get_jwt_token("super", "password")
        self.assertIsNotNone(token)
        
        # Test request with token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        url = reverse('headquarters-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_super_admin_permissions(self):
        token = self.get_jwt_token("super", "password")
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        # Can see all HQs
        url = reverse('headquarters-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertEqual(response.data['count'], 2)

        # Can create HQs
        response = self.client.post(url, {"name": "HQ Three", "location": "Loc Three"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_hq_admin_permissions(self):
        token = self.get_jwt_token("hq_admin", "password")
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        # Can only see their own HQ
        url = reverse('headquarters-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['name'], "HQ One")

        # Cannot create new HQs
        response = self.client.post(url, {"name": "HQ Three", "location": "Loc"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Can create SubHQs in their own HQ
        sub_hq_url = reverse('subheadquarters-list')
        response = self.client.post(sub_hq_url, {
            "name": "New SubHQ", "headquarters": self.hq1.id, "location": "Loc"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

       
        response = self.client.post(sub_hq_url, {
            "name": "Another HQ Sub", "headquarters": self.hq2.id, "location": "Loc"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_dashboard_api(self):
     
        token = self.get_jwt_token("super", "password")
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_hqs'], 2)
        self.assertEqual(response.data['total_sub_hqs'], 2)
        self.assertEqual(response.data['total_doctors'], 1)
        self.assertEqual(response.data['total_mrs'], 1)

        token = self.get_jwt_token("hq_admin", "password")
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_hqs'], 1)
        self.assertEqual(response.data['total_sub_hqs'], 1)
        self.assertEqual(response.data['total_doctors'], 1)
        self.assertEqual(response.data['total_mrs'], 1)
