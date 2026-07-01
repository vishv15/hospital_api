import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from accounts.models import Role
from core.models import Headquarters, SubHeadquarters, Doctor, Visit, VisitStatus

User = get_user_model()

class Command(BaseCommand):
    help = "Seeds the database with mock hospital, headquarters, users, doctors, and visits for hierarchical RBAC demonstration."

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Clearing existing data..."))
        Visit.objects.all().delete()
        Doctor.objects.all().delete()
        User.objects.all().delete()
        SubHeadquarters.objects.all().delete()
        Headquarters.objects.all().delete()

        self.stdout.write(self.style.SUCCESS("Existing data cleared successfully!"))

        # 1. Create Super Admin
        self.stdout.write("Creating Super Admin...")
        super_admin = User.objects.create_superuser(
            username="superadmin",
            email="superadmin@hospital.com",
            password="superadminpassword",
            role=Role.SUPER_ADMIN
        )
        self.stdout.write(self.style.SUCCESS(f"Super Admin created: superadmin / superadminpassword"))

        # 2. Create Headquarters
        self.stdout.write("Creating Headquarters...")
        ahmedabad_hq = Headquarters.objects.create(name="Ahmedabad HQ", location="Ahmedabad, Gujarat")
        surat_hq = Headquarters.objects.create(name="Surat HQ", location="Surat, Gujarat")

        # 3. Create Ahmedabad HQ Users
        self.stdout.write("Creating Ahmedabad HQ Users...")
        # HQ Admin
        ahmedabad_admin = User.objects.create_user(
            username="ahmedabad_admin",
            email="ahm_admin@hospital.com",
            password="ahmedabad_admin",
            role=Role.HQ_ADMIN,
            headquarters=ahmedabad_hq
        )
        # HQ Staff
        ahmedabad_staff = User.objects.create_user(
            username="ahmedabad_staff",
            email="ahm_staff@hospital.com",
            password="ahmedabad_staff",
            role=Role.HQ_STAFF,
            headquarters=ahmedabad_hq
        )

        # 4. Create Ahmedabad Sub Headquarters
        self.stdout.write("Creating Ahmedabad Sub Headquarters & Staff/MRs...")
        satellite_sub_hq = SubHeadquarters.objects.create(
            name="Satellite Sub HQ",
            headquarters=ahmedabad_hq,
            location="Satellite, Ahmedabad"
        )
        maninagar_sub_hq = SubHeadquarters.objects.create(
            name="Maninagar Sub HQ",
            headquarters=ahmedabad_hq,
            location="Maninagar, Ahmedabad"
        )

        # Satellite Sub HQ Users
        satellite_staff = User.objects.create_user(
            username="satellite_staff",
            email="sat_staff@hospital.com",
            password="satellite_staff",
            role=Role.SUB_HQ_STAFF,
            headquarters=ahmedabad_hq,
            sub_headquarters=satellite_sub_hq
        )
        satellite_mr = User.objects.create_user(
            username="satellite_mr",
            email="sat_mr@hospital.com",
            password="satellite_mr",
            role=Role.MR,
            headquarters=ahmedabad_hq,
            sub_headquarters=satellite_sub_hq
        )

        # Maninagar Sub HQ Users
        maninagar_staff = User.objects.create_user(
            username="maninagar_staff",
            email="man_staff@hospital.com",
            password="maninagar_staff",
            role=Role.SUB_HQ_STAFF,
            headquarters=ahmedabad_hq,
            sub_headquarters=maninagar_sub_hq
        )
        maninagar_mr = User.objects.create_user(
            username="maninagar_mr",
            email="man_mr@hospital.com",
            password="maninagar_mr",
            role=Role.MR,
            headquarters=ahmedabad_hq,
            sub_headquarters=maninagar_sub_hq
        )

        # 5. Create Ahmedabad Doctors & Visits
        self.stdout.write("Creating Doctors & Visits for Ahmedabad...")
        
        # Satellite Doctors
        dr_sharma = Doctor.objects.create(
            name="Sharma", specialization="Cardiologist", phone="9876543210", email="sharma@hospital.com",
            headquarters=ahmedabad_hq, sub_headquarters=satellite_sub_hq
        )
        dr_sharma.assigned_mrs.add(satellite_mr)

        dr_patel = Doctor.objects.create(
            name="Patel", specialization="Pediatrician", phone="9876543211", email="patel@hospital.com",
            headquarters=ahmedabad_hq, sub_headquarters=satellite_sub_hq
        )
        dr_patel.assigned_mrs.add(satellite_mr)

        # Maninagar Doctors
        dr_joshi = Doctor.objects.create(
            name="Joshi", specialization="Dermatologist", phone="9876543212", email="joshi@hospital.com",
            headquarters=ahmedabad_hq, sub_headquarters=maninagar_sub_hq
        )
        dr_joshi.assigned_mrs.add(maninagar_mr)

        # Visits
        today = timezone.localtime(timezone.now()).date()
        yesterday = today - datetime.timedelta(days=1)
        tomorrow = today + datetime.timedelta(days=1)

        # Satellite MR visits
        Visit.objects.create(mr=satellite_mr, doctor=dr_sharma, date=today, status=VisitStatus.PENDING, notes="Follow up checkup")
        Visit.objects.create(mr=satellite_mr, doctor=dr_patel, date=yesterday, status=VisitStatus.COMPLETED, notes="Delivered samples")
        Visit.objects.create(mr=satellite_mr, doctor=dr_sharma, date=tomorrow, status=VisitStatus.PENDING, notes="Introduction call")

        # Maninagar MR visits
        Visit.objects.create(mr=maninagar_mr, doctor=dr_joshi, date=today, status=VisitStatus.COMPLETED, notes="Product discussion")

        # 6. Create Surat HQ Users & Data
        self.stdout.write("Creating Surat HQ Users & Data...")
        # HQ Admin
        surat_admin = User.objects.create_user(
            username="surat_admin",
            email="sur_admin@hospital.com",
            password="surat_admin",
            role=Role.HQ_ADMIN,
            headquarters=surat_hq
        )
        # HQ Staff
        surat_staff = User.objects.create_user(
            username="surat_staff",
            email="sur_staff@hospital.com",
            password="surat_staff",
            role=Role.HQ_STAFF,
            headquarters=surat_hq
        )

        adajan_sub_hq = SubHeadquarters.objects.create(
            name="Adajan Sub HQ",
            headquarters=surat_hq,
            location="Adajan, Surat"
        )
        adajan_mr = User.objects.create_user(
            username="adajan_mr",
            email="adj_mr@hospital.com",
            password="adajan_mr",
            role=Role.MR,
            headquarters=surat_hq,
            sub_headquarters=adajan_sub_hq
        )

        dr_shah = Doctor.objects.create(
            name="Shah", specialization="Neurologist", phone="9876543213", email="shah@hospital.com",
            headquarters=surat_hq, sub_headquarters=adajan_sub_hq
        )
        dr_shah.assigned_mrs.add(adajan_mr)

        Visit.objects.create(mr=adajan_mr, doctor=dr_shah, date=today, status=VisitStatus.PENDING, notes="Initial pitch")

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))

        # Output Table of Credentials
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("MOCK USER CREDENTIALS FOR TESTING")
        self.stdout.write("=" * 60)
        self.stdout.write(f"{'Role':<20} | {'Username':<18} | {'Password':<18}")
        self.stdout.write("-" * 60)
        self.stdout.write(f"{'Super Admin':<20} | {'superadmin':<18} | {'superadminpassword':<18}")
        self.stdout.write(f"{'Ahmedabad Admin':<20} | {'ahmedabad_admin':<18} | {'ahmedabad_admin':<18}")
        self.stdout.write(f"{'Ahmedabad Staff':<20} | {'ahmedabad_staff':<18} | {'ahmedabad_staff':<18}")
        self.stdout.write(f"{'Satellite Staff':<20} | {'satellite_staff':<18} | {'satellite_staff':<18}")
        self.stdout.write(f"{'Satellite MR':<20} | {'satellite_mr':<18} | {'satellite_mr':<18}")
        self.stdout.write(f"{'Maninagar Staff':<20} | {'maninagar_staff':<18} | {'maninagar_staff':<18}")
        self.stdout.write(f"{'Maninagar MR':<20} | {'maninagar_mr':<18} | {'maninagar_mr':<18}")
        self.stdout.write(f"{'Surat Admin':<20} | {'surat_admin':<18} | {'surat_admin':<18}")
        self.stdout.write(f"{'Surat Staff':<20} | {'surat_staff':<18} | {'surat_staff':<18}")
        self.stdout.write(f"{'Adajan MR':<20} | {'adajan_mr':<18} | {'adajan_mr':<18}")
        self.stdout.write("=" * 60 + "\n")
