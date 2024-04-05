
from django.utils.translation import gettext_lazy as _


PENDING_THERAPIST = 'PENDING_THERAPIST'
PENDING_PATIENT = 'PENDING_PATIENT'
CONFIRMED = 'CONFIRMED'
CANCELLED_BY_THERAPIST = 'CANCELLED_BY_THERAPIST'
CANCELLED_BY_PATIENT = 'CANCELLED_BY_PATIENT'
REJECTED = 'REJECTED'
COMPLETED = 'COMPLETED'
MISSED = 'MISSED'
PENDING_SURVEY_RESPONSE = 'PENDING_SURVEY_RESPONSE'

# all possible stati of an appointment
APPOINTMENT_STATUS_CHOICES = {
    PENDING_THERAPIST: _('Pending Therapist'), ## waiting for the therapist to confirm the patient request
    PENDING_SURVEY_RESPONSE: _('Pending Survey Response'), ## waiting for the patient to finish the survey, if the target timeslot had an assigned survey
    PENDING_PATIENT: _('Pending Patient'), ## waiting for the patient to confirm therapist's invite
    CONFIRMED: _('Confirmed'), ## both parties confirmed the appointment
    CANCELLED_BY_PATIENT: _('Cancelled By Patient'), ## patient cancelled the appointment
    CANCELLED_BY_THERAPIST: _('Cancelled By Therapist'), ## therapist cancelled the appointment
    COMPLETED: _('Completed'), ## both parties showed up and the appointment was completed
    }

UPDATEABLE_APPOINTMENT_STATI = [
    'PENDING_THERAPIST',
    'PENDING_PATIENT',
    'CONFIRMED'
]

# all statuses that flag the manual cancellation of an appointment
CANCELLED_APPOINTMENT_STATUSES = [CANCELLED_BY_PATIENT, CANCELLED_BY_THERAPIST]

PENDING_APPOINTMENT_STATUSES= [PENDING_THERAPIST, PENDING_PATIENT, PENDING_SURVEY_RESPONSE]

RESERVED_APPOINTMENT_STATUSES= [PENDING_THERAPIST, PENDING_PATIENT, PENDING_SURVEY_RESPONSE, CONFIRMED]

PENDING = 'PENDING'
ACCEPTED = 'ACCEPTED'
REJECTED = 'REJECTED'

# stati of a a referral request
REFERRAL_STATUS_CHOICES = {
    PENDING: _('Pending'), ## waiting for the therapist to accept or reject the referral
    ACCEPTED: _('Accepted'), ## the referee accepted the referral
    REJECTED: _('Rejected'), ## the referee rejected the referral
}

ACTIVE = 'ACTIVE'
INACTIVE = 'INACTIVE'
# stati of a therapist assignment
THERAPIST_ASSIGNMENT_STATUS_CHOICES = {
    ACTIVE: _('Active'), ## waiting for the therapist to accept or reject the assignment
    INACTIVE: _('Inactive'), ## the therapist accepted
}


REFERRER_FIELD = 'referrer'
REFEREE_FIELD = 'referee'

REFERRER_OR_REFEREE_FIELD = [REFERRER_FIELD, REFEREE_FIELD]

PATIENT_FIELD = 'patient'

WEEK_DAYS = [
    'sunday'
    'monday',
    'tuesday',
    'wednesday',
    'thursday',
    
]