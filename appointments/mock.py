"""
    File used for object mocking for all appointment system related tasks
"""
from typing import List
import faker
import appointments
from appointments.constants.enums import APPOINTMENT_STATUS_CHOICES, REFERRAL_STATUS_CHOICES

from appointments.models import Appointment, AppointmentFeedback, AvailabilityTimeSlot, PatientReferralRequest
from core.models import StudentPatient, Therapist
from django.utils import timezone


faker = faker.Faker()

class AvailabilityTimeslotMocker:
    """
        Mocking utility for availability timeslots
    """
    
    @staticmethod
    def mock_availability_timeslots(n: int=5):
        """
            Mock n availability timeslots
        """
        
        therapists = Therapist.objects.all()[:2]

        availability_timeslots = []
        for i in range(n):
            start_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0) + timezone.timedelta(days=i)
            end_date = timezone.now().replace(hour=23, minute=0, second=0, microsecond=0) + timezone.timedelta(days=i)

            random_start_date = faker.date_time_between(start_date, end_date)
            availability_timeslots.append(
                AvailabilityTimeSlot(
                    therapist=therapists[0],
                    start_at= random_start_date,
                    end_at= faker.date_time_between(random_start_date, end_date),
                )
            )

            random_start_date = faker.date_time_between(start_date, end_date)
            availability_timeslots.append(
                AvailabilityTimeSlot(
                    therapist=therapists[1],
                    start_at= random_start_date,
                    end_at= faker.date_time_between(random_start_date, end_date),
                )
            )
        
        return AvailabilityTimeSlot.objects.bulk_create(availability_timeslots)


class AppointmentMocker:
    """
        Mocking utility for appointments
    """
    
    @staticmethod
    def mock_appointments(n: int = 5):
        """
            Mock appointments along their therapist assignments
        """
        AvailabilityTimeSlot.objects.all().delete()
        Appointment.objects.all().delete()
        timeslots = AvailabilityTimeslotMocker.mock_availability_timeslots(n)
        patients = StudentPatient.objects.all()[:n]
        appointments = []
        
        for i, availability_timeslot in enumerate(timeslots):
            appointments.append(
                Appointment(
                    timeslot=availability_timeslot,
                    patient=patients[i % n],
                    status=APPOINTMENT_STATUS_CHOICES['CONFIRMED']
                )
                )


            
        return Appointment.objects.bulk_create(appointments)

    @staticmethod
    def mock_appointment_feedbacks( appointments: List[Appointment]):
        """
            Mock n appointment feedbacks for each passed appointment
        """
        feedbacks =[]

        for appointment in appointments:
            feedbacks.append(
                AppointmentFeedback(
                    appointment=appointment,
                    rating=faker.random_int(min=1, max=5),
                    comment=faker.sentence()
                )
            )

        return AppointmentFeedback.objects.bulk_create(feedbacks)



class ReferralMocker:
    """
        Mocking utility for referrals
    """
    
    @staticmethod
    def mock_referral_requests(appointments: List[Appointment]):
        """
            Mock n referral requests, and corresponding appointments
        """
        
        referral_requests = []
        for appointment in appointments:
            referral_requests.append(
                PatientReferralRequest(
                    referrer=appointment.patient.user,
                    referee=appointment.timeslot.therapist.user,
                    reason=faker.sentence(),
                    status=REFERRAL_STATUS_CHOICES['PENDING'],
                    responding_therapist=appointment.timeslot.therapist
                )
            )

        return PatientReferralRequest.objects.bulk_create(referral_requests)

