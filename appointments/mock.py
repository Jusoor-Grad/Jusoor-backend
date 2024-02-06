"""
    File used for object mocking for all appointment system related tasks
"""
from typing import List
import faker
import appointments
from appointments.constants.enums import APPOINTMENT_STATUS_CHOICES, REFERRAL_STATUS_CHOICES

from appointments.models import Appointment, AppointmentFeedback, AppointmentReferral, AvailabilityTimeSlot, AvailabilityTimeSlotGroup, PatientReferralRequest, TherapistAssignment
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
        slot_groups = []
        slot_groups.extend([
            AvailabilityTimeSlotGroup(),
            AvailabilityTimeSlotGroup()]

        )
        for i in range(n):
            # randomizing start and end dates of each slot to be constrained on different days to avoid conflicts
            start_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0) + timezone.timedelta(days=i)
            end_date = timezone.now().replace(hour=23, minute=0, second=0, microsecond=0) + timezone.timedelta(days=i)

            random_start_date = faker.date_time_between(start_date, end_date)
            availability_timeslots.append(
                AvailabilityTimeSlot(
                    therapist=therapists[0],
                    start_at= random_start_date,
                    end_at= faker.date_time_between(random_start_date, end_date),
                    group=slot_groups[0]
                )
            )

            random_start_date = faker.date_time_between(start_date, end_date)
            availability_timeslots.append(
                AvailabilityTimeSlot(
                    therapist=therapists[1],
                    start_at= random_start_date,
                    end_at= faker.date_time_between(random_start_date, end_date),
                    group=slot_groups[1]
                )
            )
        AvailabilityTimeSlotGroup.objects.bulk_create(slot_groups)
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
        # TODO: remove after verifying correctness of initial mocking
        AvailabilityTimeSlot.objects.all().delete()
        Appointment.objects.all().delete()
        timeslots = AvailabilityTimeslotMocker.mock_availability_timeslots(n)
        patients = StudentPatient.objects.all()[:n]
        appointments = []
        appoint_assignments = []
        
        for i, availability_timeslot in enumerate(timeslots):
            appointments.append(
                Appointment(
                    timeslot=availability_timeslot,
                    patient=patients[i % n],
                    status=APPOINTMENT_STATUS_CHOICES['CONFIRMED'],
                    start_at=availability_timeslot.start_at,
                    end_at=availability_timeslot.end_at
                )
                )
            appoint_assignments.append(
                TherapistAssignment(
                    appointment=appointments[i],
                    therapist_timeslot=availability_timeslot,
                    status='Active'
                )
            )
        

        appointment_outs= Appointment.objects.bulk_create(appointments)
        TherapistAssignment.objects.bulk_create(appoint_assignments)
        return appointment_outs

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
        
        referrals_outs = []
        appointment_referrals = []
        for appointment in appointments:
            referral_request= PatientReferralRequest(
                    referrer=appointment.patient.user,
                    referee=appointment.timeslot.therapist.user,
                    reason=faker.sentence(),
                    status=REFERRAL_STATUS_CHOICES['PENDING'],
                    responding_therapist=appointment.timeslot.therapist
                )
                
            referrals_outs.append(
                referral_request
            )

            appointment_referrals.append(
                AppointmentReferral(
                    referral_request=referral_request,
                    appointment=appointment
                )
            )

        referrals_outs = PatientReferralRequest.objects.bulk_create(referrals_outs)
        appointment_referrals = AppointmentReferral.objects.bulk_create(appointment_referrals)
        return referrals_outs, appointment_referrals
