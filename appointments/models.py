from random import choice
from django.db import models
from pydantic import validator
from appointments.constants.enums import APPOINTMENT_STATUS_CHOICES, REFERRAL_STATUS_CHOICES
from authentication.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import Therapist, TimeStampedModel



## ------------------ Core models ------------------ ##

class AvailabilityTimeSlot(TimeStampedModel):
    """
        Recording assigned avialability times for a therapist
    """

    therapist = models.ForeignKey(Therapist, on_delete=models.PROTECT, null=False, blank=False)
    start_at = models.DateTimeField(null= False, blank=False)
    end_at = models.DateTimeField(null= False, blank=False)


class Appointment(TimeStampedModel):
    """
        Recording appointment requests on a pre-defind availability slot
    """
    
    timeslot = models.ForeignKey(AvailabilityTimeSlot, on_delete=models.PROTECT, related_name='linked_appointments')
    patient = models.ForeignKey('core.StudentPatient', on_delete=models.PROTECT, related_name='appointments')
    status = models.CharField(max_length=20, blank=False, null=False, choices=APPOINTMENT_STATUS_CHOICES.items())



class PatientReferralRequest(TimeStampedModel):
    """
        Record for a referral from one user to another for a therapist
    """

    referrer = models.ForeignKey(User, on_delete=models.PROTECT, related_name='outward_referrals')
    referee = models.ForeignKey(User, on_delete=models.PROTECT, related_name='inward_referrals')
    reason = models.TextField(null=False, blank=False)
    status = models.CharField(max_length=20, blank=False, null=False, choices=REFERRAL_STATUS_CHOICES.items())
    # the therapist who responded to the referral request
    responding_therapist = models.ForeignKey(Therapist, on_delete=models.PROTECT, related_name='referrals', null=False, blank=False)

    def __str__(self):
        return f'Referral {self.pk} from {self.referrer.id} to {self.referee.id}'

class AppointmentReferral(TimeStampedModel):
    """
        Recording all appointments originating from a referral
    """

    referral_request = models.ForeignKey(PatientReferralRequest, on_delete=models.PROTECT, related_name='appointments_referrals', blank=False, null=False)
    appointment = models.ForeignKey(Appointment, on_delete=models.PROTECT, related_name='referrals', blank=False, null=False)

    def __str__(self):
        return f'Referral {self.referral_request.id} -> Appointment {self.appointment.id}'

## ------------------ Utility models ------------------ ##

class AppointmentFeedback(TimeStampedModel):
    """
        Record for feedback recieved in response to a completed appointment
    """

    appointment = models.ForeignKey(Appointment, on_delete=models.PROTECT, related_name='feedbacks', blank=False, null=False)
    rating = models.IntegerField(null=False, blank=False, default=5, validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'Feedback for appointment {self.appointment.id} ({self.rating}/5) : {self.comment}'

class TherapistAssignment(TimeStampedModel):
    """
        Record to audit the shift of an appointment assignment from one therapist to another
    """

    therapist = models.ForeignKey(Therapist, on_delete=models.PROTECT, null=False, blank=False, related_name='appointment_assignments')
    status = models.CharField(max_length=20, blank=False, null=False, choices=APPOINTMENT_STATUS_CHOICES.items())
    appointment = models.ForeignKey(Appointment, on_delete=models.PROTECT, null=False, blank=False, related_name='therapist_assignments')
    