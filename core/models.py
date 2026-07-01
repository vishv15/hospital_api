from django.db import models
from django.conf import settings

class Headquarters(models.Model):
    name = models.CharField(max_length=255, unique=True)
    location = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Headquarters"

    def __str__(self):
        return self.name

class SubHeadquarters(models.Model):
    name = models.CharField(max_length=255)
    headquarters = models.ForeignKey(
        Headquarters,
        on_delete=models.CASCADE,
        related_name='sub_hqs'
    )
    location = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Sub Headquarters"
        unique_together = ('name', 'headquarters')

    def __str__(self):
        return f"{self.name} ({self.headquarters.name})"

class Doctor(models.Model):
    name = models.CharField(max_length=255)
    specialization = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    
    # Hierarchical assignment of Doctor
    headquarters = models.ForeignKey(
        Headquarters,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='doctors'
    )
    sub_headquarters = models.ForeignKey(
        SubHeadquarters,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='doctors'
    )
    
    # Assigned Medical Representatives
    assigned_mrs = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='assigned_doctors'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dr. {self.name} - {self.specialization}"

class VisitStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    COMPLETED = 'COMPLETED', 'Completed'

class Visit(models.Model):
    mr = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='visits'
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name='visits'
    )
    date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=VisitStatus.choices,
        default=VisitStatus.PENDING
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Visit by {self.mr.username} to {self.doctor.name} on {self.date}"
