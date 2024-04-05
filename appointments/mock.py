"""
    File used for object mocking for all appointment system related tasks
"""
from tkinter import ACTIVE
from typing import List
import faker
from appointments.constants.enums import APPOINTMENT_STATUS_CHOICES, CONFIRMED, PENDING, PENDING_SURVEY_RESPONSE, REFERRAL_STATUS_CHOICES

from appointments.models import Appointment,  AvailabilityTimeSlot, AvailabilityTimeSlotGroup, PatientReferralRequest, TherapistAssignment
from core.mock import PatientMock, TherapistMock
from core.models import StudentPatient, Therapist
from django.utils import timezone

from core.types import TimeInterval, WeeklyTimeSchedule
from surveys.mock import TherapistSurveyMocker


faker = faker.Faker()

class AvailabilityTimeslotMocker:
    """
        Mocking utility for availability timeslots
    """
    
    @staticmethod
    def mock_instances(n: int=5, fixed_therapist: Therapist = None, with_survey: bool = False):
        """
            Mock n availability timeslots
        """
        
        therapists = [fixed_therapist] if fixed_therapist else TherapistMock.mock_instances(n)

        availability_timeslots = []
        slot_groups = []
        slot_groups.extend([
            AvailabilityTimeSlotGroup(),
            AvailabilityTimeSlotGroup()]

        )
        for i in range(n):
            # randomizing start and end dates of each slot to be constrained on different days to avoid conflicts
            start_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0) + timezone.timedelta(days=i+1) ## adding an extra day to avoid past-date errors in testing validation
            end_date = timezone.now().replace(hour=23, minute=0, second=0, microsecond=0) + timezone.timedelta(days=i+  1)
            random_start_date = faker.date_time_between(start_date, end_date)
            availability_timeslots.append(
                AvailabilityTimeSlot(
                    therapist=therapists[i % len(therapists) if len(therapists) > 1 else 0],
                    start_at= random_start_date,
                    end_at= faker.date_time_between(random_start_date, end_date),
                    group=slot_groups[0],
                    entry_survey = TherapistSurveyMocker.mock_instances(1)[0] if with_survey else None
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
    def mock_instances(n: int = 5, fixed_patient: StudentPatient = None, fixed_therapist: Therapist = None, with_survey: bool = False):
        """
            Mock appointments along their therapist assignments
        """
        # TODO: remove after verifying correctness of initial mocking
        timeslots = AvailabilityTimeslotMocker.mock_instances(n, fixed_therapist=fixed_therapist, with_survey=with_survey)
        patients = [fixed_patient] if fixed_patient else  PatientMock.mock_instances(n)
        appointments = []
        appoint_assignments = []
        appointment_surveys = []
        
        for i, availability_timeslot in enumerate(timeslots):
            appointments.append(
                Appointment(
                    timeslot=availability_timeslot,
                    patient=patients[i % len(patients) if len(patients) > 1 else 0],
                    status=CONFIRMED if not availability_timeslot.entry_survey else PENDING_SURVEY_RESPONSE,
                    start_at=availability_timeslot.start_at,
                    end_at=availability_timeslot.end_at
                )
                )
            appoint_assignments.append(
                TherapistAssignment(
                    appointment=appointments[i],
                    therapist_timeslot=availability_timeslot,
                    status=ACTIVE
                )
            )

            if availability_timeslot.entry_survey:
                appointment_surveys.append(
                    TherapistSurveyMocker.mock_instances(
                        survey_n=1
                    )[0]
                )
        

        appointment_outs= Appointment.objects.bulk_create(appointments)
        TherapistAssignment.objects.bulk_create(appoint_assignments)
        return appointment_outs

    



class ReferralMocker:
    """
        Mocking utility for referrals
    """
    
    @staticmethod
    def mock_referral_requests(appointments: List[Appointment], fixed_referrer: StudentPatient = None, fixed_referee: Therapist = None):
        """
            Mock n referral requests, and corresponding appointments
        """

        # TODO: remove dependency on appointments when mocking referral requests
        
        referrals_outs = []
        for appointment in appointments:
            referral_request= PatientReferralRequest(
                    referee= fixed_referee.user if fixed_referee else appointment.patient.user,
                    referrer= fixed_referrer.user if fixed_referrer else appointment.timeslot.therapist.user,
                    reason=faker.sentence(),
                    status=PENDING,
                    responding_therapist=appointment.timeslot.therapist,
                    appointment=appointment
                )
                
            referrals_outs.append(
                referral_request
            )

        return PatientReferralRequest.objects.bulk_create(referrals_outs)
        