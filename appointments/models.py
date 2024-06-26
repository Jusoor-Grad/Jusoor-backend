from django.db import models
from pydantic import validator
from appointments.constants.enums import APPOINTMENT_STATUS_CHOICES, CANCELLED_APPOINTMENT_STATUSES, REFERRAL_STATUS_CHOICES, THERAPIST_ASSIGNMENT_STATUS_CHOICES
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import Therapist, TimeStampedModel
from surveys.enums import CANCELLED
from surveys.models import TherapistSurvey, TherapistSurveyResponse

## ------------------ Core models ------------------ ##


class AvailabilityTimeSlotGroup(TimeStampedModel):
    """
        Representation of a group of availability
        timeslots created together by the therapist
    """
    pass

class AvailabilityTimeSlot(TimeStampedModel):
    """
        a continuous time interval where a therapist can be available
        to receive appointments by students
    """

    therapist = models.ForeignKey(Therapist, on_delete=models.PROTECT, null=False, blank=False)
    start_at = models.DateTimeField(null= False, blank=False)
    end_at = models.DateTimeField(null= False, blank=False)
    group   = models.ForeignKey(AvailabilityTimeSlotGroup, on_delete=models.PROTECT, null=True, blank=True)
    active = models.BooleanField(default=True)
    # survey assigned by survey to evaluate patient status before conducting the appointment
    entry_survey = models.ForeignKey(TherapistSurvey, on_delete=models.PROTECT, null=True, blank=True, related_name='availability_timeslots')

    def __str__(self):
        return f'Availability timeslot {self.pk} for therapist {self.therapist.id}'
    


class Appointment(TimeStampedModel):
    """
        an appointment created to signify a meeting between a therapist and a patient in
        a pre-specified time interval
    """
    
    timeslot = models.ForeignKey(AvailabilityTimeSlot, on_delete=models.PROTECT, related_name='linked_appointments', null= True, blank=True)
    patient = models.ForeignKey('core.StudentPatient', on_delete=models.PROTECT, related_name='appointments')
    status = models.CharField(max_length=40, blank=False, null=False, choices=APPOINTMENT_STATUS_CHOICES.items())
    start_at = models.DateTimeField(null= True, blank=True)
    end_at = models.DateTimeField(null= True, blank=True)

    def save(self, *args, **kwargs) -> None:

        if self.status in CANCELLED_APPOINTMENT_STATUSES and hasattr(self, 'survey_response'):
            # why not simply update? to avoid wasting an extra DB pass when the status is not already cancelled
            if self.survey_response.status != CANCELLED:
                self.survey_response.status = CANCELLED
                self.survey_response.save()

        return super().save(*args, **kwargs)
    
class AppointmentSurveyResponse(TimeStampedModel):
    """
        joint table to create a direct link between the status of the linked
        survey response and the appointment of a patient
    """

    appointment = models.OneToOneField(Appointment, on_delete=models.PROTECT, related_name='survey_response')
    survey_response = models.OneToOneField(TherapistSurveyResponse, on_delete=models.PROTECT, related_name='linked_appointment')
    survey= models.ForeignKey(TherapistSurvey, on_delete=models.PROTECT, related_name='appointment_responses')

    def __str__(self):
        return f'Survey response {self.survey_response.id} for appointment {self.appointment.id}'
    
    



class PatientReferralRequest(TimeStampedModel):
    """
        Record for a referral from one student user to another to create a therapist appointment
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
        a model to record the shift of the appointment assignment from one therapist to another
    """

    therapist_timeslot = models.ForeignKey(AvailabilityTimeSlot, on_delete=models.PROTECT, null=False, blank=False, related_name='appointment_assignments')
    status = models.CharField(max_length=20, blank=False, null=False, choices=THERAPIST_ASSIGNMENT_STATUS_CHOICES.items())
    appointment = models.ForeignKey(Appointment, on_delete=models.PROTECT, null=False, blank=False, related_name='therapist_assignments')
    