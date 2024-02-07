from django.utils.translation import gettext_lazy as _



# all possible stati of an appointment
APPOINTMENT_STATUS_CHOICES = {
    'PENDING_THERAPIST': _('Pending Therapist'), ## waiting for the therapist to confirm the patient request
    'PENDING_PATIENT': _('Pending Patient'), ## waiting for the patient to confirm therapist's invite
    'CONFIRMED': _('Confirmed'), ## both parties confirmed the appointment
    'CANCELLED': _('Cancelled'), ## one party cancelled the appointment after it was confirmed
    'REJECTED': _('Rejected'), ## the invited party rejected the invitation
    'COMPLETED': _('Completed'), ## both parties showed up and the appointment was completed
    'MISSED': _('Missed'), ## one of the parties did not show up
}

UPDATEABLE_APPOINTMENT_STATI = [
    'PENDING_THERAPIST',
    'PENDING_PATIENT',
    'CONFIRMED'
]


# stati of a a referral request
REFERRAL_STATUS_CHOICES = {
    'PENDING': _('Pending'), ## waiting for the therapist to accept or reject the referral
    'ACCEPTED': _('Accepted'), ## the referee accepted the referral
    'REJECTED': _('Rejected'), ## the referee rejected the referral
}

# stati of a therapist assignment
THERAPIST_ASSIGNMENT_STATUS_CHOICES = {
    'ACTIVE': _('Active'), ## waiting for the therapist to accept or reject the assignment
    'REJECTED': _('Rejected'), ## the therapist accepted
}