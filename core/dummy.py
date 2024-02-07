from appointments.models import Appointment
from core.enums import UserRole
from core.querysets import ConditionalQuerySet, OwnedQuerySet


res = ConditionalQuerySet(
        {
             UserRole.PATIENT: OwnedQuerySet(Appointment.objects.all(), ['patient'], 'patient_profile'), 
             UserRole.THERAPIST: Appointment.objects.all()
             })
print(res)