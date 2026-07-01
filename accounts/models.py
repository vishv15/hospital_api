from django.db import models
from django.contrib.auth.models import AbstractUser

class Role(models.TextChoices):
    SUPER_ADMIN = 'SUPER_ADMIN', 'Super Admin'
    HQ_ADMIN = 'HQ_ADMIN', 'HQ Admin'
    HQ_STAFF = 'HQ_STAFF', 'HQ Staff'
    SUB_HQ_STAFF = 'SUB_HQ_STAFF', 'Sub HQ Staff'
    MR = 'MR', 'Medical Representative'

class User(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.MR
    )
    # Headquarters assigned to the user
    # (Super Admin doesn't have one, HQ Admin/Staff must have one, Sub HQ Staff/MR can have one)
    headquarters = models.ForeignKey(
        'core.Headquarters',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )
    # Sub Headquarters assigned to the user
    # (Sub HQ Staff and MRs can be assigned directly to a Sub Headquarters)
    sub_headquarters = models.ForeignKey(
        'core.SubHeadquarters',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
