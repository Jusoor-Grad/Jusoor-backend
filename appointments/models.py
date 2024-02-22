from random import choice
from click import group
from django.db import models
from pydantic import validator
from appointments.constants.enums import APPOINTMENT_STATUS_CHOICES, REFERRAL_STATUS_CHOICES, THERAPIST_ASSIGNMENT_STATUS_CHOICES
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import Therapist, TimeStampedModel

## ------------------ Core models ------------------ ##


class AvailabilityTimeSlotGroup(TimeStampedModel):
    """
        Recording assigned avialability times for a therapist
    """
    pass

class AvailabilityTimeSlot(TimeStampedModel):
    """
        Grouping availability timeslots to allow batch editing
    """

    therapist = models.ForeignKey(Therapist, on_delete=models.PROTECT, null=False, blank=False)
    start_at = models.DateTimeField(null= False, blank=False)
    end_at = models.DateTimeField(null= False, blank=False)
    group   = models.ForeignKey(AvailabilityTimeSlotGroup, on_delete=models.PROTECT, null=True, blank=True)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f'Availability timeslot {self.pk} for therapist {self.therapist.id}'
    


class Appointment(TimeStampedModel):
    """
        Recording appointment requests on a pre-defined availability slot
    """
    
    timeslot = models.ForeignKey(AvailabilityTimeSlot, on_delete=models.PROTECT, related_name='linked_appointments', null= True, blank=True)
    patient = models.ForeignKey('core.StudentPatient', on_delete=models.PROTECT, related_name='appointments')
    status = models.CharField(max_length=40, blank=False, null=False, choices=APPOINTMENT_STATUS_CHOICES.items())
    start_at = models.DateTimeField(null= True, blank=True)
    end_at = models.DateTimeField(null= True, blank=True)
    



class PatientReferralRequest(TimeStampedModel):
    """
        Record for a referral from one user to another for a therapist
    """

    referrer = models.ForeignKey('authentication.User', on_delete=models.PROTECT, related_name='outward_referrals')
    referee = models.ForeignKey('authentication.User', on_delete=models.PROTECT, related_name='inward_referrals')
    reason = models.TextField(null=False, blank=False)
    status = models.CharField(max_length=20, blank=False, null=False, choices=REFERRAL_STATUS_CHOICES.items())
    # the therapist who responded to the referral request
    responding_therapist = models.ForeignKey(Therapist, on_delete=models.PROTECT, related_name='referrals', null=True, blank=True)
    appointment = models.ForeignKey(Appointment, on_delete=models.PROTECT, blank=True, null=True, related_name='referral_request')

    def __str__(self):
        return f'Referral {self.pk} from {self.referrer.id} to {self.referee.id}'


## ------------------ Utility models ------------------ ##

class TherapistAssignment(TimeStampedModel):
    """
        Record to audit the shift of an appointment assignment from one therapist to another
    """

    therapist_timeslot = models.ForeignKey(AvailabilityTimeSlot, on_delete=models.PROTECT, null=False, blank=False, related_name='appointment_assignments')
    status = models.CharField(max_length=20, blank=False, null=False, choices=THERAPIST_ASSIGNMENT_STATUS_CHOICES.items())
    appointment = models.ForeignKey(Appointment, on_delete=models.PROTECT, null=False, blank=False, related_name='therapist_assignments')
    