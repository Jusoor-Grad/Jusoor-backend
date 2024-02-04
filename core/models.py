"""
General utility DB models
"""

from django.db import models
from django.contrib.auth import get_user_model
from core.db_managers import SoftDeletedManager

# Create your models here.


class TimeStampedModel(models.Model):
    """
    Abstract model to add tracking timestamps to all models
    in addition to soft_deletion functionality
    """
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeletedManager() ## custom object manager to mask out soft deleted objects

    class Meta:
        """
        Meta class for the model
        """
        abstract = True



class Therapist(TimeStampedModel):
    """
        Model store store therapist-specific information for therapist users
    """

    user = models.OneToOneField(get_user_model(), unique=True, on_delete=models.CASCADE, related_name='therapist_profile')
    bio = models.TextField(null=True, blank=True)
    speciality = models.CharField(max_length=100, null=True, blank=True)


    def __str__(self) -> str:
        return f'Therapist: {self.user.username}'


class StudentPatient(TimeStampedModel):

    user = models.OneToOneField(get_user_model(), unique=True, on_delete=models.PROTECT, related_name='patient_profile')
    department = models.ForeignKey('KFUPMDepartment', on_delete=models.PROTECT, related_name='students')


class KFUPMDepartment(models.Model):
    """
    Model to store the department of a student
    """
    short_name = models.CharField(max_length=10, unique=True)
    long_name = models.CharField(max_length=100, unique=True)

    def __str__(self) -> str:
        return self.short_name
