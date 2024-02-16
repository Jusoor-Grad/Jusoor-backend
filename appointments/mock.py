"""
    File used for object mocking for all appointment system related tasks
"""
from datetime import time
from tracemalloc import start
from typing import List
import faker
import appointments
from appointments.constants.enums import APPOINTMENT_STATUS_CHOICES, REFERRAL_STATUS_CHOICES

from appointments.models import Appointment,  AvailabilityTimeSlot, AvailabilityTimeSlotGroup, PatientReferralRequest, TherapistAssignment
from core.models import StudentPatient, Therapist
from django.utils import timezone

from core.types import TimeInterval, WeeklyTimeSchedule


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

    @staticmethod
    def mock_schedule_input(days: List[str] = ['sunday'], conflicting: bool = False):
        """
            mocking a weekly schedule input for batch creationg of timeslots
        """
        output = dict()
        for day in days:
            start_at= timezone.now().replace(hour=1, minute=0, second=0, microsecond=0)
            end_at= start_at + timezone.timedelta(hours=1)
            output[day] = []

            output[day].append(
                    TimeInterval(
                        start_at=start_at.time(),
                        end_at=end_at.time()
                    )
                )
            if not conflicting:
                start_at+= timezone.timedelta(hours=1, minutes=30)
                end_at= start_at + timezone.timedelta(minutes=10)
            else:
                start_at+= timezone.timedelta(hours=0, minutes=30)
                end_at= start_at + timezone.timedelta(hours=0, minutes=10)

            output[day].append(
                    TimeInterval(
                        start_at=start_at.time(),
                        end_at=end_at.time()
                    )
                )
       
        return WeeklyTimeSchedule(**output)

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
        for appointment in appointments:
            referral_request= PatientReferralRequest(
                    referee=appointment.patient.user,
                    referrer=appointment.timeslot.therapist.user,
                    reason=faker.sentence(),
                    status=REFERRAL_STATUS_CHOICES['PENDING'],
                    responding_therapist=appointment.timeslot.therapist,
                    appointment=appointment
                )
                
            referrals_outs.append(
                referral_request
            )

        return PatientReferralRequest.objects.bulk_create(referrals_outs)
        