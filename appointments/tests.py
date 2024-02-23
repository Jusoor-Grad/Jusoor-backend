from datetime import datetime, timedelta
from turtle import st
from django import conf
from django.test import TestCase, tag
from faker import Faker
from django.utils import timezone
from tomlkit import date
from appointments.constants.enums import ACTIVE, CANCELLED_BY_PATIENT, CANCELLED_BY_THERAPIST, COMPLETED, CONFIRMED, INACTIVE, PENDING, PENDING_THERAPIST, REJECTED
from appointments.models import Appointment, AvailabilityTimeSlotGroup, PatientReferralRequest, TherapistAssignment
from dateutil import rrule
from core.mock import PatientMock, TherapistMock
from core.utils.testing import auth_request
from .mock import AppointmentMocker, AvailabilityTimeslotMocker, ReferralMocker
# Create your tests here.
from appointments.views import AppointmentsViewset, AvailabilityTimeSlot, AvailabilityTimeslotViewset, ReferralViewset
from rest_framework.test import APIRequestFactory

@tag('apptmnts')
class AppointmentsTests(TestCase):

	def setUp(self) -> None:
		viewset = AppointmentsViewset
		self.list = viewset.as_view({'get': 'list'})
		self.retrieve = viewset.as_view({'get': 'retrieve'})
		self.create = viewset.as_view({'post': 'create'})
		self.update = viewset.as_view({'put': 'update'})
		self.partial_update = viewset.as_view({'patch': 'partial_update'})
		self.cancel = viewset.as_view({'patch': 'cancel'})
		self.complete = viewset.as_view({'patch': 'complete'})
		self.faker = Faker(locale='ar_EG')

	
	@tag('list-apptmnts-owned')
	def test_list_own_appointments(self):     
		#  mock patient
		patient = PatientMock.mock_instances(n=1)[0]
		# mock appointments
		appointments = AppointmentMocker.mock_instances(n=5, fixed_patient=patient)
		# mock request
		request = auth_request(APIRequestFactory().get, f'appointments/', user=patient.user)
		response = self.list(request)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(response.data['results']), 5)


	@tag('list-apptmnts-non-owned')
	def test_list_non_owned_appointments(self):
		
		#  mock patient
		patients = PatientMock.mock_instances(n=2)
		# mock appointments
		appointments = AppointmentMocker.mock_instances(n=5, fixed_patient=patients[0])
		# mock request
		request = auth_request(APIRequestFactory().get, f'appointments/', user=patients[1].user)
		response = self.list(request)
		
		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(response.data['results']), 0)

	@tag('retrieve-apptmnt-owned')
	def test_retrieve_own_appointment(self):
		#  mock patient
		patient = PatientMock.mock_instances(n=1)[0]
		# mock appointments
		appointments = AppointmentMocker.mock_instances(n=5, fixed_patient=patient)
		# mock request
		request = auth_request(APIRequestFactory().get, f'appointments/{appointments[0].id}/', user=patient.user)
		response = self.retrieve(request, pk=appointments[0].id)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['id'], appointments[0].id)

	
	@tag('retrieve-apptmnt-non-owned')
	def test_retrieve_non_owned_appointment(self):
		#  mock patient
		patients = PatientMock.mock_instances(n=2)
		# mock appointments
		appointments = AppointmentMocker.mock_instances(n=5, fixed_patient=patients[0])
		# mock request
		request = auth_request(APIRequestFactory().get, f'appointments/{appointments[0].id}/', user=patients[1].user)
		response = self.retrieve(request, pk=appointments[0].id)

		self.assertEqual(response.status_code, 404)

	@tag('create-apptmnt-valid-by-patient')
	def test_create_appointment_valid_by_patient(self):
		#  mock patient
		patient = PatientMock.mock_instances(n=1)[0]
		# mock timeslot
		timeslot = AvailabilityTimeslotMocker.mock_instances(n=1)[0]
		# mock a valid JSON within the timeslot boundaries        
		start_at = self.faker.date_time_between(start_date=timeslot.start_at, end_date=timeslot.end_at)
		end_at =self.faker.date_time_between(start_date=start_at, end_date=timeslot.end_at)

		body = {
			'timeslot': timeslot.id,
			'patient': patient.user.id,
			'start_at': start_at,
			'end_at': end_at
		}

		# mock request
		request = auth_request(APIRequestFactory().post, f'appointments/', user=patient.user, body=body)
		response = self.create(request)

		

		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.data['patient'], patient.id)
		self.assertTrue(Appointment.objects.filter(id=response.data['id']).exists())

	@tag('create-apptmnt-valid-by-therapist')
	def test_create_appointment_valid_by_therapist(self):
		#  mock patient
		therapist =TherapistMock.mock_instances(n=1)[0]
		patient = PatientMock.mock_instances(n=1)[0]
		# mock timeslot
		timeslot = AvailabilityTimeslotMocker.mock_instances(n=1)[0]
		# mock an valid JSON within the timeslot boundaries        
		start_at = self.faker.date_time_between(start_date=timeslot.start_at, end_date=timeslot.end_at)
		end_at =self.faker.date_time_between(start_date=start_at, end_date=timeslot.end_at)

		body = {
			'timeslot': timeslot.id,
			'patient': patient.user.id,
			'start_at': start_at,
			'end_at': end_at
		}

		# mock request
		request = auth_request(APIRequestFactory().post, f'appointments/', user=timeslot.therapist.user, body=body)
		response = self.create(request)

		

		self.assertEqual(response.status_code, 201)
		self.assertEqual(response.data['patient'], patient.id)
		self.assertTrue(Appointment.objects.filter(id=response.data['id']).exists())

	@tag('create-apptmnt-nonexisting-timeslot-by-patient')
	def test_create_appointment_invalid_timeslot_by_patient(self):
		#  mock patient
		patient = PatientMock.mock_instances(n=1)[0]
		# mock timeslot
		timeslot = AvailabilityTimeslotMocker.mock_instances(n=1)[0]
		# mock a valid JSON within the timeslot boundaries        
		start_at = self.faker.date_time_between(start_date=timeslot.start_at, end_date=timeslot.end_at - timedelta(minutes=5))
		end_at =self.faker.date_time_between(start_date=start_at, end_date=timeslot.end_at)

		body = {
			'timeslot':  145455, ## non-existing appointment id in test db
			'patient': patient.user.id,
			'start_at': start_at,
			'end_at': end_at
		}

		# mock request
		request = auth_request(APIRequestFactory().post, f'appointments/', user=patient.user, body=body)
		response = self.create(request)

		

		self.assertEqual(response.status_code, 400)

	@tag('create-apptmnt-invalid-other-therapist-timeslot-by-therapist')
	def test_create_appointment_invalid_other_therapist_timeslot_by_therapist(self):
		#  mock patient
		therapists =TherapistMock.mock_instances(n=2)
		patient = PatientMock.mock_instances(n=1)[0]
		# mock timeslot
		timeslot = AvailabilityTimeslotMocker.mock_instances(n=1, fixed_therapist=therapists[0])[0]
		# mock an valid JSON within the timeslot boundaries        
		start_at = self.faker.date_time_between(start_date=timeslot.start_at, end_date=timeslot.end_at)
		end_at =self.faker.date_time_between(start_date=start_at, end_date=timeslot.end_at)

		body = {
			'timeslot': timeslot.id,
			'patient': patient.user.id,
			'start_at': start_at,
			'end_at': end_at
		}

		# mock request
		request = auth_request(APIRequestFactory().post, f'appointments/', user=therapists[1].user, body=body)
		response = self.create(request)

		

		self.assertEqual(response.status_code, 400)

	@tag('create-apptmnt-invalid-past-timeslot-by-patient')
	def test_create_appointment_invalid_past_timeslot_by_patient(self):
		#  mock patient
		patient = PatientMock.mock_instances(n=1)[0]
		# mock timeslot
		timeslot = AvailabilityTimeslotMocker.mock_instances(n=1)[0]
		# mock a valid JSON within the timeslot boundaries        
		start_at = self.faker.date_time_between(start_date=timeslot.start_at - timedelta(days=5), end_date=timeslot.end_at - timedelta(days=5))
		end_at =self.faker.date_time_between(start_date=start_at, end_date=timeslot.end_at)

		body = {
			'timeslot': timeslot.id,
			'patient': patient.user.id,
			'start_at': start_at,
			'end_at': end_at
		}

		# mock request
		request = auth_request(APIRequestFactory().post, f'appointments/', user=patient.user, body=body)
		response = self.create(request)

		

		self.assertEqual(response.status_code, 400)

	@tag('create-apptmnt-invalid-conflict-apptmnt-by-therapist')
	def test_create_appointment_invalid_conflict_appointment_by_patient(self):

		#  mock patient
		therapists =TherapistMock.mock_instances(n=1)
		patient = PatientMock.mock_instances(n=1)[0]
		# mock timeslot
		# create an existing conflicting appointment
		timeslot = AvailabilityTimeSlot.objects.create(
			therapist=therapists[0],
			start_at=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)+ timedelta(days=1),
			end_at=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(hours=12, days=1)
		)
		apptmnt_start_at = self.faker.date_time_between(start_date=timeslot.start_at, end_date=timeslot.end_at)
		apptmnt_end_at = self.faker.date_time_between(start_date=apptmnt_start_at, end_date=timeslot.end_at)
		appointment = Appointment.objects.create(
			patient=patient,
			timeslot=timeslot,
			start_at= apptmnt_start_at,
			status=CONFIRMED,
			end_at= apptmnt_end_at)   
	  
		start_at = self.faker.date_time_between(start_date=appointment.start_at, end_date=appointment.end_at)
		# mock an valid JSON within the timeslot boundaries        
		end_at =self.faker.date_time_between(start_date=start_at, end_date=appointment.end_at)

		

		body = {
			'timeslot': appointment.timeslot.id,
			'patient': patient.user.id,
			'start_at': start_at,
			'end_at': end_at
		}

		# mock request
		request = auth_request(APIRequestFactory().post, f'appointments/', user=patient.user, body=body)
		response = self.create(request)

		

		self.assertEqual(response.status_code, 400)


	@tag('update-apptmnt-valid-by-patient')
	def test_update_appointment_valid_by_patient(self):
		#  mock patient
		patient = PatientMock.mock_instances(n=1)[0]
		therapists = TherapistMock.mock_instances(n=1)
		# mock appointments
		timeslot = AvailabilityTimeSlot.objects.create(
			therapist=therapists[0],
			start_at=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)+ timedelta(days=1),
			end_at=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(hours=12, days=1)
		)
		apptmnt_start_at = self.faker.date_time_between(start_date=timeslot.start_at, end_date=timeslot.end_at)
		apptmnt_end_at = self.faker.date_time_between(start_date=apptmnt_start_at, end_date=timeslot.end_at)
		appointment = Appointment.objects.create(
			patient=patient,
			timeslot=timeslot,
			start_at= apptmnt_start_at,
			status=CONFIRMED,
			end_at= apptmnt_end_at)   
		
		# mock a valid JSON within the timeslot boundaries        
		start_at = self.faker.date_time_between(start_date=appointment.timeslot.start_at, end_date=appointment.timeslot.end_at)
		end_at =self.faker.date_time_between(start_date=start_at, end_date=appointment.timeslot.end_at )

		body = {
			'start_at': start_at,
			'end_at': end_at
		}

		# mock request
		request = auth_request(APIRequestFactory().put, f'appointments/{appointment.id}/', user=patient.user, body=body)
		response = self.update(request, pk=appointment.id)

		

		self.assertEqual(response.status_code, 200)
		self.assertTrue(Appointment.objects.filter(id=appointment.id, start_at=start_at, end_at=end_at).exists())

	@tag('update-apptmnt-valid-by-therapist')
	def test_update_appointment_valid_by_therapist(self):
		
		# mock patient
		therapist =TherapistMock.mock_instances(n=1)[0]
		patient = PatientMock.mock_instances(n=1)[0]
		# mock appointments
		timeslot = AvailabilityTimeSlot.objects.create(
			therapist=therapist,
			start_at=datetime.now()+ timedelta(days=1),
			end_at=datetime.now() + timedelta(days=1, hours=3))
		appointment = Appointment.objects.create(
			patient=patient,
			timeslot= timeslot,
			start_at=timezone.now() + timedelta(days=1),
			end_at=timezone.now() + timedelta(days=1, hours=1),
			status=CONFIRMED
			)
		# mock a valid JSON within the timeslot boundaries
		start_at = self.faker.date_time_between(start_date=appointment.timeslot.start_at, end_date=appointment.timeslot.end_at)
		end_at =self.faker.date_time_between(start_date=start_at, end_date=appointment.timeslot.end_at )

		body = {
			'start_at': start_at,
			'end_at': end_at,
			'timeslot': None
		}

		# mock request
		request = auth_request(APIRequestFactory().put, f'appointments/{appointment.id}/', user=therapist.user, body=body)
		response = self.update(request, pk=appointment.id)


		self.assertEqual(response.status_code, 200)
		self.assertTrue(Appointment.objects.filter(id=appointment.id, start_at=start_at, end_at=end_at).exists())

	@tag('update-apptmnt-invalid-boundaries')
	def test_update_apptmnt_invalid_boundaries(self):
		
		# mock patient
		therapist =TherapistMock.mock_instances(n=1)[0]
		patient = PatientMock.mock_instances(n=1)[0]
		# mock appointments
		timeslot = AvailabilityTimeSlot.objects.create(
			therapist=therapist,
			start_at=datetime.now(),
			end_at=datetime.now() + timedelta(days=1)
		)
		apptmnt_start_at = self.faker.date_time_between(start_date=timeslot.start_at, end_date=timeslot.end_at)
		apptmnt_end_at = self.faker.date_time_between(start_date=apptmnt_start_at, end_date=timeslot.end_at)
		appointment = Appointment.objects.create(
			patient=patient,
			timeslot=timeslot,
			start_at= apptmnt_start_at,
			status=CONFIRMED,
			end_at= apptmnt_end_at)
		# mock a valid JSON within the timeslot boundaries
		start_at = self.faker.date_time_between(start_date=appointment.timeslot.start_at + timedelta(days=1), end_date=appointment.timeslot.end_at + timedelta(days=1))
		end_at =self.faker.date_time_between(start_date=start_at, end_date=appointment.timeslot.end_at + timedelta(days=1))

		body = {
			'start_at': start_at,
			'end_at': end_at
		}

		# mock request
		request = auth_request(APIRequestFactory().put, f'appointments/{appointment.id}/', user=therapist.user, body=body)
		response = self.update(request, pk=appointment.id)

		

		self.assertEqual(response.status_code, 400)


	@tag('update-apptmnt-conflicting-apptmnt')
	def test_update_apptmnt_conflicting_apptmnt(self):
		
		# mock patient
		therapist =TherapistMock.mock_instances(n=1)[0]
		patient = PatientMock.mock_instances(n=1)[0]
		# mock appointments
		timeslot = AvailabilityTimeSlot.objects.create(
			therapist=therapist,
			start_at=datetime.now(),
			end_at=datetime.now() + timedelta(days=1)
		)

		apt_start_at = self.faker.date_time_between(start_date=timeslot.start_at, end_date=timeslot.end_at- timedelta(hours=12))
		apt_end_at = self.faker.date_time_between(start_date=apt_start_at, end_date=timeslot.end_at - timedelta(hours=12))
		appointment_one = Appointment.objects.create(
			patient=patient,
			timeslot=timeslot,
			start_at= apt_start_at ,
			end_at= apt_end_at,
			status=CONFIRMED
		)

		apt_start_at = self.faker.date_time_between(start_date=timeslot.start_at + timedelta(hours=12), end_date=timeslot.end_at)
		apt_end_at = self.faker.date_time_between(start_date=apt_start_at, end_date=timeslot.end_at)
		conflicting_appointment = Appointment.objects.create(
			patient=patient,
			timeslot=timeslot,
			start_at= apt_start_at ,
			end_at= apt_end_at,
			status=CONFIRMED
		)

		
		

		# mock a valid JSON within the timeslot boundaries
		start_at = conflicting_appointment.start_at
		end_at = conflicting_appointment.end_at

		body = {
			'start_at': start_at,
			'end_at': end_at
		}

		# mock request
		request = auth_request(APIRequestFactory().put, f'appointments/{appointment_one.id}/', user=therapist.user, body=body)
		response = self.update(request, pk=appointment_one.id)

		

		self.assertEqual(response.status_code, 400)

	@tag('update-apptmnt-other-therapist')
	def test_update_apptmnt_non_owning_therapist(self):
		
		# mock patient
		therapists =TherapistMock.mock_instances(n=2)
		patient = PatientMock.mock_instances(n=1)[0]
		# mock appointments
		appointment = Appointment.objects.create(
			patient=patient,
			timeslot=AvailabilityTimeslotMocker.mock_instances(n=1, fixed_therapist=therapists[0])[0],
			start_at=timezone.now() + timedelta(days=1),
			end_at=timezone.now() + timedelta(days=1, hours=1),
			status=CONFIRMED
			)
		# mock a valid JSON within the timeslot boundaries
		start_at = self.faker.date_time_between(start_date=appointment.start_at, end_date=appointment.timeslot.end_at)
		end_at =self.faker.date_time_between(start_date=start_at, end_date=appointment.timeslot.end_at )

		body = {
			'start_at': start_at,
			'end_at': end_at
		}

		# mock request
		request = auth_request(APIRequestFactory().put, f'appointments/{appointment.id}/', user=therapists[1].user, body=body)
		response = self.update(request, pk=appointment.id)

		

		self.assertEqual(response.status_code, 404)

	@tag('cancel-apptmnt-valid')
	def test_cancel_apptmnt_valid(self):
		
		# mock patient
		patient = PatientMock.mock_instances(n=1)[0]
		# mock appointments
		appointment = Appointment.objects.create(
			patient=patient,
			timeslot=AvailabilityTimeslotMocker.mock_instances(n=1)[0],
			start_at=timezone.now() + timedelta(days=1),
			end_at=timezone.now() + timedelta(days=1, hours=1),
			status=CONFIRMED
			)
		

		# mock request
		request = auth_request(APIRequestFactory().patch, f'appointments/{appointment.id}/cancel/', user=patient.user)
		response = self.cancel(request, pk=appointment.id)

		

		self.assertEqual(response.status_code, 200)
		self.assertTrue(Appointment.objects.filter(id=appointment.id, status=CANCELLED_BY_PATIENT).exists())

		# testing cancelling from therapist

		# mock patient
		therapist = TherapistMock.mock_instances(n=1)[0]
		# mock appointments
		appointment = AppointmentMocker.mock_instances(n=1, fixed_therapist=therapist)[0]

		# mock request
		request = auth_request(APIRequestFactory().patch, f'appointments/{appointment.id}/cancel/', user=therapist.user)
		response = self.cancel(request, pk=appointment.id)

		

		self.assertEqual(response.status_code, 200)
		self.assertTrue(Appointment.objects.filter(id=appointment.id, status=CANCELLED_BY_THERAPIST).exists())

	@tag('complete-apptmnt-valid')
	def test_complete_apptmnt_valid(self):

		# mock patient
		patient = PatientMock.mock_instances(n=1)[0]
		therapist = TherapistMock.mock_instances(n=1)[0]
		
		# mock appointments
		appointment = Appointment.objects.create(
			patient=patient,
			timeslot=AvailabilityTimeslotMocker.mock_instances(n=1, fixed_therapist= therapist)[0],
			start_at=timezone.now() - timedelta(days=1),
			end_at=timezone.now() - timedelta(hours=23),
			status=CONFIRMED
			)
		

		# mock request
		request = auth_request(APIRequestFactory().patch, f'appointments/{appointment.id}/complete/', user=therapist.user)
		response = self.complete(request, pk=appointment.id)



		self.assertEqual(response.status_code, 200)
		self.assertTrue(Appointment.objects.filter(id=appointment.id, status=COMPLETED).exists())

	@tag('complete-apptmnt-invalid-not-confirmed')
	def test_complete_apptmnt_invalid_not_confirmed(self):
			
		# mock patient
		patient = PatientMock.mock_instances(n=1)[0]
		therapist = TherapistMock.mock_instances(n=1)[0]
		
		# mock appointments
		appointment = Appointment.objects.create(
			patient=patient,
			timeslot=AvailabilityTimeslotMocker.mock_instances(n=1, fixed_therapist= therapist)[0],
			start_at=timezone.now() - timedelta(days=1),
			end_at=timezone.now() - timedelta(hours=23),
			status=PENDING_THERAPIST
			)
		

		# mock request
		request = auth_request(APIRequestFactory().patch, f'appointments/{appointment.id}/complete/', user=therapist.user)
		response = self.complete(request, pk=appointment.id)


		self.assertEqual(response.status_code, 404)
		
	@tag('complete-apptmnt-invalid-future-start')
	def test_complete_apptmnt_invalid_future_start(self):
			
		# mock patient
		patient = PatientMock.mock_instances(n=1)[0]
		therapist = TherapistMock.mock_instances(n=1)[0]
		
		# mock appointments
		appointment = Appointment.objects.create(
			patient=patient,
			timeslot=AvailabilityTimeslotMocker.mock_instances(n=1, fixed_therapist= therapist)[0],
			start_at=timezone.now() + timedelta(days=1),
			end_at=timezone.now() + timedelta(days=1, hours=1),
			status=CONFIRMED
			)
		

		# mock request
		request = auth_request(APIRequestFactory().patch, f'appointments/{appointment.id}/complete/', user=therapist.user)
		response = self.complete(request, pk=appointment.id)



		self.assertEqual(response.status_code, 400)


@tag('referral-requests')
class TestReferralRequests(TestCase):

	def setUp(self) -> None:
		viewset = ReferralViewset
		self.list = viewset.as_view({'get': 'list'})
		self.retrieve = viewset.as_view({'get': 'retrieve'})
		self.create = viewset.as_view({'post': 'create'})
		self.update = viewset.as_view({'put': 'update'})
		self.reply = viewset.as_view({'patch': 'reply'})
		self.faker = Faker(locale='ar_EG')

	@tag('list-referrals-patient')
	def test_list_patient_referrals(self):
		
		# mock 2 patients
		patients = PatientMock.mock_instances(n=2)
		# mock appointments
		appointments = AppointmentMocker.mock_instances(n=5, fixed_patient=patients[0])
		# mock referrals
		referrals = ReferralMocker.mock_referral_requests(appointments, fixed_referrer=patients[0])
		# mock request
		request = auth_request(APIRequestFactory().get, f'referrals/', user=patients[0].user)
		response = self.list(request)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(response.data['results']), 5)
		


	@tag('list-referrals-therapist')
	def test_list_referrals_therapist(self):
		
		patients = PatientMock.mock_instances(n=2)
		therapist = TherapistMock.mock_instances(n=1)[0]
		# mock appointments
		appointments = AppointmentMocker.mock_instances(n=5, fixed_patient=patients[1])
		# mock referrals
		referrals = ReferralMocker.mock_referral_requests(appointments, fixed_referrer=patients[0])
		# mock request
		request = auth_request(APIRequestFactory().get, f'referrals/', user=therapist.user)
		response = self.list(request)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(response.data['results']), 5)

	@tag('retrieve-referrals-valid-patient')
	def test_retrieve_referrals_patient(self):
		
		patients = PatientMock.mock_instances(n=2)
		# mock appointments
		appointments = AppointmentMocker.mock_instances(n=5, fixed_patient=patients[1])
		# mock referrals
		referrals = ReferralMocker.mock_referral_requests(appointments, fixed_referrer=patients[0])
		# mock request
		request = auth_request(APIRequestFactory().get, f'referrals/{referrals[0].id}/', user=patients[0].user)
		response = self.retrieve(request, pk=referrals[0].id)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['id'], referrals[0].id)


	@tag('retrieve-referrals-valid-therapist')
	def test_retrrieve_referrals_therapist(self):
			
		patients = PatientMock.mock_instances(n=2)
		therapist = TherapistMock.mock_instances(n=1)[0]
		# mock appointments
		appointments = AppointmentMocker.mock_instances(n=5, fixed_patient=patients[1])
		# mock referrals
		referrals = ReferralMocker.mock_referral_requests(appointments, fixed_referrer=patients[0])
		# mock request
		request = auth_request(APIRequestFactory().get, f'referrals/{referrals[0].id}/', user=therapist.user)
		response = self.retrieve(request, pk=referrals[0].id)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['id'], referrals[0].id)
	
	@tag('create-referral-request-valid')
	def test_valid_create_referral(self):
		
		patients = PatientMock.mock_instances(n=2)
		therapist = TherapistMock.mock_instances(n=1)[0]
		# mock request
		body = {
			'referee': patients[1].user.id,
			'reason': self.faker.text()
		}

		request = auth_request(APIRequestFactory().post, f'referrals/', user=patients[0].user, body=body)
		response = self.create(request)

		

		self.assertEqual(response.status_code, 201)
		self.assertTrue(PatientReferralRequest.objects.filter(id=response.data['id']).exists())

	@tag('create-referral-invalid-duplicate')
	def test_create_duplicate_referral(self):
		
		patients = PatientMock.mock_instances(n=2)
		therapist = TherapistMock.mock_instances(n=1)[0]
		# mock request
		body = {
			'referee': patients[1].user.id,
			'reason': self.faker.text()
		}
		# creating 2 referrals to a single referee
		request = auth_request(APIRequestFactory().post, f'referrals/', user=patients[0].user, body=body)
		response = self.create(request)

		request = auth_request(APIRequestFactory().post, f'referrals/', user=patients[0].user, body=body)
		response = self.create(request)

		self.assertEqual(response.status_code, 400)

	@tag('update-referral-valid')
	def test_update_valid_referral(self):
		
		patients = PatientMock.mock_instances(n=2)
		therapist = TherapistMock.mock_instances(n=1)[0]
		# mock appointments
		referral_request = PatientReferralRequest.objects.create(
			referee=patients[1].user,
			referrer=patients[0].user,
			reason=self.faker.text(),
			status=PENDING
		)
		# mock request
		body = {
			'reason': self.faker.text(),
			'referee': patients[1].user.id
		}

		request = auth_request(APIRequestFactory().put, f'referrals/{referral_request.id}/', user=patients[0].user, body=body)
		response = self.update(request, pk=referral_request.id)

		

		self.assertEqual(response.status_code, 200)
		self.assertTrue(PatientReferralRequest.objects.filter(id=referral_request.id, reason = body['reason']).exists())

	@tag('update-referral-invalid-not-pending')
	def test_update_referral_not_pending(self):
		
		patients = PatientMock.mock_instances(n=2)
		therapist = TherapistMock.mock_instances(n=1)[0]
		# mock a confirmed referral request
		referral_request = PatientReferralRequest.objects.create(
			referee=patients[0].user,
			referrer=therapist.user,
			reason=self.faker.text(),
			status=REJECTED
		)
		
		# mock request
		body = {
			'reason': self.faker.text()
		}

		request = auth_request(APIRequestFactory().put, f'referrals/{referral_request.id}/', user=patients[0].user, body=body)
		response = self.update(request, pk=referral_request.id)

		self.assertEqual(response.status_code, 404)

	@tag('reply-valid-therapist')
	def test_valid_reply_therapist(self):
		
		patients = PatientMock.mock_instances(n=2)
		therapist = TherapistMock.mock_instances(n=1)[0]
		# mock appointments
		referral_request = PatientReferralRequest.objects.create(
			referee=patients[1].user,
			referrer=patients[0].user,
			reason=self.faker.text(),
			status=PENDING
		)
		# mock request
		body = {
			'status': REJECTED
		}

		request = auth_request(APIRequestFactory().patch, f'referrals/{referral_request.id}/reply/', user=therapist.user, body=body)
		response = self.reply(request, pk=referral_request.id)

		self.assertEqual(response.status_code, 200)
		self.assertTrue(PatientReferralRequest.objects.filter(id=referral_request.id, status=REJECTED).exists())

	@tag('reply-invalid-patient')
	def test_invalid_reply_patient(self):
		
		patients = PatientMock.mock_instances(n=2)
		therapist = TherapistMock.mock_instances(n=1)[0]
		# mock appointments
		referral_request = PatientReferralRequest.objects.create(
			referee=patients[1].user,
			referrer=patients[0].user,
			reason=self.faker.text(),
			status=PENDING
		)
		# mock request
		body = {
			'status': REJECTED
		}

		request = auth_request(APIRequestFactory().patch, f'referrals/{referral_request.id}/reply/', user=patients[0].user, body=body)
		response = self.reply(request, pk=referral_request.id)

		self.assertEqual(response.status_code, 403)

	


@tag('timeslots')
class TestAvailabilityTimeslot(TestCase):

	def setUp(self) -> None:
		viewset = AvailabilityTimeslotViewset
		self.list = viewset.as_view({'get': 'list'})
		self.retrieve = viewset.as_view({'get': 'retrieve'})
		self.create = viewset.as_view({'post': 'create'})
		self.batch_create = viewset.as_view({'post': 'batch_create'})
		self.update = viewset.as_view({'put': 'update'})
		self.batch_update = viewset.as_view({'put': 'batch_update'})
		self.destroy = viewset.as_view({'delete': 'destroy'})
		self.faker = Faker(locale='ar_EG')

	@tag('list-valid')
	def test_valid_list(self):
		
		# mock therapist
		therapists = TherapistMock.mock_instances(n=1)[0]

		# mock timeslots
		timeslots = AvailabilityTimeslotMocker.mock_instances(n=5)
		
		# mock request
		request = auth_request(APIRequestFactory().get, f'timeslots/', user=therapists.user)
		response = self.list(request)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(response.data['results']), 5)

	@tag('retrieve-valid')
	def test_valid_retrieve(self):
		
		# mock therapist
		therapists = TherapistMock.mock_instances(n=1)[0]

		# mock timeslots
		timeslot = AvailabilityTimeslotMocker.mock_instances(n=1)[0]
		
		# mock request
		request = auth_request(APIRequestFactory().get, f'timeslots/{timeslot.id}/', user=therapists.user)
		response = self.retrieve(request, pk=timeslot.id)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.data['id'], timeslot.id)


	@tag('create-valid')
	def test_valid_create(self):
		
		# mock therapist
		therapists = TherapistMock.mock_instances(n=1)[0]
		# mock request
		body = {
			'therapist': therapists.id,
			'intervals': [
				{
					'start_at': timezone.now(),
					'end_at': timezone.now() + timedelta(hours=1)
				},
				{
					'start_at': timezone.now() + timedelta(hours=3),
					'end_at': timezone.now() + timedelta(hours=4)
				} 
			]
		}

		request = auth_request(APIRequestFactory().post, f'timeslots/', user=therapists.user, body=body)
		response = self.create(request)

		self.assertEqual(response.status_code, 201)
		self.assertEqual(AvailabilityTimeSlot.objects.all().count(), 2)

	@tag('create-invalid-interval-input')
	def test_invalid_create_interval_input(self):
		
		# mock therapist
		therapists = TherapistMock.mock_instances(n=1)[0]
		# mock request
		body = {
			'therapist': therapists.id,
			'intervals': [
				{
					'start_at': timezone.now(),
					'end_at': timezone.now() + timedelta(hours=1)
				}, {
					'start_at': timezone.now(),
					'end_at': timezone.now() + timedelta(minutes=30)
				}
			]
		}

		request = auth_request(APIRequestFactory().post, f'timeslots/', user=therapists.user, body=body)
		response = self.create(request)

		self.assertEqual(response.status_code, 400)

	@tag('create-invalid-existing-conflict')
	def test_invalid_create_conflict_timeslot(self):
			
			# mock therapist
			therapist = TherapistMock.mock_instances(n=1)[0]
			# mock timeslots
			timeslot = AvailabilityTimeSlot.objects.create(
				therapist=therapist,
				start_at=timezone.now(),
				end_at=timezone.now() + timedelta(hours=1),
				active=True
			)
			# mock request
			body = {
				'therapist': therapist.id,
				'intervals': [
					{
						'start_at': timeslot.start_at,
						'end_at': timeslot.end_at
					}
				]
			}
	
			request = auth_request(APIRequestFactory().post, f'timeslots/', user=therapist.user, body=body)
			response = self.create(request)

			self.assertEqual(response.status_code, 400)

	@tag('batch-create-valid')
	def test_valid_batch_create(self):
			
			# mock therapist
			therapists = TherapistMock.mock_instances(n=1)[0]
			# get the first coming sunday using dateutil rrule
			sunday: datetime = rrule.rrule(rrule.WEEKLY, dtstart=timezone.now(), byweekday=rrule.SU, count=1)[0]
			start_at= sunday.replace(hour=0, minute=0, second=0)

			end_at = start_at + timedelta(days=14)
			# mock request
			body = {
				'therapist': therapists.id,
				'start_at': start_at,
				'end_at': end_at,
				'weekly_schedule': {
				
				'sunday': [
				{
					'start_at': timezone.now().replace(hour=0, second=0, minute=0).time(),
					'end_at': (timezone.now().replace(hour=0, second=0, minute=0) + timedelta(hours=1)).time()
				}, {
					'start_at': (timezone.now().replace(hour=0, second=0, minute=0) + timedelta(hours=3)).time(),
					'end_at': (timezone.now().replace(hour=0, second=0, minute=0) + timedelta(hours=4)).time()
				}
			], 
			'monday': [
				{
					'start_at': timezone.now().replace(hour=0, second=0, minute=0).replace().time(),
					'end_at': (timezone.now().replace(hour=0, second=0, minute=0) + timedelta(hours=1)).time()
				}, {
					'start_at': (timezone.now().replace(hour=0, second=0, minute=0) + timedelta(hours=3)).time(),
					'end_at': (timezone.now().replace(hour=0, second=0, minute=0) + timedelta(hours=4)).time()
				}
			]
			
			}
			}
			
	
			request = auth_request(APIRequestFactory().post, f'timeslots/batch_create/', user=therapists.user, body=body)
			response = self.batch_create(request)

			
	
			self.assertEqual(response.status_code, 201)
			self.assertEqual(AvailabilityTimeSlot.objects.all().count(), 8)

	@tag('batch-create-invalid-interval-input')
	def test_invalid_batch_create_interval_input(self):
		# mock therapist
			therapists = TherapistMock.mock_instances(n=1)[0]
			# get the first coming sunday using dateutil rrule
			sunday: datetime = rrule.rrule(rrule.WEEKLY, dtstart=timezone.now(), byweekday=rrule.SU, count=1)[0]
			start_at= sunday.replace(hour=0, minute=0, second=0)

			end_at = start_at + timedelta(days=14)
			# mock request
			body = {
				'therapist': therapists.id,
				'start_at': start_at,
				'end_at': end_at,
				'weekly_schedule': {
				
				'sunday': [
				{
					'start_at': timezone.now().replace(hour=0, second=0, minute=0).time(),
					'end_at': (timezone.now().replace(hour=0, second=0, minute=0) + timedelta(hours=1)).time()
				}, {
					'start_at': (timezone.now().replace(hour=0, second=0, minute=0) + timedelta(minutes=30)).time(),
					'end_at': (timezone.now().replace(hour=0, second=0, minute=0) + timedelta(hours=1)).time()
				}
			], 
			'monday': [
				{
					'start_at': timezone.now().replace(hour=0, second=0, minute=0).replace().time(),
					'end_at': (timezone.now().replace(hour=0, second=0, minute=0) + timedelta(hours=1)).time()
				}, {
					'start_at': (timezone.now().replace(hour=0, second=0, minute=0) + timedelta(hours=3)).time(),
					'end_at': (timezone.now().replace(hour=0, second=0, minute=0) + timedelta(hours=4)).time()
				}
			]
			
			}
			}
			
	
			request = auth_request(APIRequestFactory().post, f'timeslots/batch_create/', user=therapists.user, body=body)
			response = self.batch_create(request)

			
	
			self.assertEqual(response.status_code, 400)
			self.assertEqual(AvailabilityTimeSlot.objects.all().count(), 0)

	@tag('batch-create-invalid-existing-conflict')
	def test_invalid_batch_create_conflict(self):
		
		# mock therapist
		therapists = TherapistMock.mock_instances(n=1)[0]
		# get the first coming sunday using dateutil rrule
		sunday: datetime = rrule.rrule(rrule.WEEKLY, dtstart=timezone.now(), byweekday=rrule.SU, count=1)[0]
		start_at= sunday.replace(hour=0, minute=0, second=0)
		end_at = start_at + timedelta(days=14)
		# mock conflicting timeslot
		timeslot = AvailabilityTimeSlot.objects.create(
			therapist=therapists,
			start_at= sunday.replace(hour=1, minute=0, second=0),
			end_at= sunday.replace(hour=2, minute=0, second=0)
		)

		# mock request
		body = {
				'therapist': therapists.id,
				'start_at': start_at,
				'end_at': end_at,
				'weekly_schedule': {
				
				'sunday': [
				{
					'start_at': timezone.now().replace(hour=0, second=0, minute=0).time(),
					'end_at': (timezone.now().replace(hour=0, second=0, minute=0) + timedelta(hours=1)).time()
				}, {
					'start_at': (timezone.now().replace(hour=0, second=0, minute=0) + timedelta(minutes=30)).time(),
					'end_at': (timezone.now().replace(hour=0, second=0, minute=0) + timedelta(hours=1)).time()
				}
			], 
			'monday': [
				{
					'start_at': timezone.now().replace(hour=0, second=0, minute=0).replace().time(),
					'end_at': (timezone.now().replace(hour=0, second=0, minute=0) + timedelta(hours=1)).time()
				}, {
					'start_at': (timezone.now().replace(hour=0, second=0, minute=0) + timedelta(hours=3)).time(),
					'end_at': (timezone.now().replace(hour=0, second=0, minute=0) + timedelta(hours=4)).time()
				}
			]
			
			}
			}
		
		request = auth_request(APIRequestFactory().post, f'timeslots/batch_create/', user=therapists.user, body=body)
		response = self.batch_create(request)

		

		self.assertEqual(response.status_code, 400)
		self.assertEqual(AvailabilityTimeSlot.objects.all().count(), 1)
		

	@tag('update-valid')
	def test_valid_update(self):
		
		# mock therapist
		therapists = TherapistMock.mock_instances(n=1)[0]
		# mock timeslots
		group = AvailabilityTimeSlotGroup.objects.create()
		timeslot = AvailabilityTimeSlot.objects.create(
			therapist=therapists,
			start_at=timezone.now() + timedelta(days=1),
			end_at=timezone.now() + timedelta(days=2),
			group=group

		)
		# link mocked appointment
		apptmnt_start_at = self.faker.date_time_between(start_date=timeslot.start_at, end_date=timeslot.end_at)
		apptmnt_end_at = self.faker.date_time_between(start_date=apptmnt_start_at, end_date=timeslot.end_at)
		appointment = Appointment.objects.create(
			patient=PatientMock.mock_instances(n=1)[0],
			timeslot=timeslot,
			start_at= apptmnt_start_at,
			end_at = apptmnt_end_at
			)


		
		# mock request
		body = {
			'start_at': self.faker.date_time_between(start_date=timeslot.start_at, end_date=appointment.start_at).time(),
			'end_at': self.faker.date_time_between(start_date=appointment.end_at, end_date=timeslot.end_at).time()
		}

		request = auth_request(APIRequestFactory().put, f'timeslots/{timeslot.id}/', user=therapists.user, body=body)
		response = self.update(request, pk=timeslot.id)

		

		self.assertEqual(response.status_code, 200)
		self.assertTrue(AvailabilityTimeSlot.objects.filter(id=timeslot.id, start_at__time=body['start_at'], end_at__time=body['end_at'], group=None).exists())

	@tag('update-valid-force-drop')
	def test_valid_update_force_drop(self):
		
		# mock therapist
		therapists = TherapistMock.mock_instances(n=1)[0]
		# mock timeslots
		group = AvailabilityTimeSlotGroup.objects.create()
		timeslot = AvailabilityTimeSlot.objects.create(
			therapist=therapists,
			start_at=timezone.now().replace(hour=0, minute=0, second=0)  + timedelta(days=1),
			end_at=timezone.now().replace(hour=0, minute=0, second=0) + timedelta(days=1, hours=4),
			group=group

		)
		# link mocked appointment
		apptmnt_start_at = self.faker.date_time_between(start_date=timeslot.start_at, end_date=timeslot.end_at)
		apptmnt_end_at = self.faker.date_time_between(start_date=apptmnt_start_at, end_date=timeslot.end_at)
		appointment = Appointment.objects.create(
			patient=PatientMock.mock_instances(n=1)[0],
			timeslot=timeslot,
			start_at= apptmnt_start_at,
			end_at = apptmnt_end_at,
			)
		
		assignment = TherapistAssignment.objects.create(
			therapist_timeslot=timeslot,
			appointment=appointment,
			status=ACTIVE
		)

		# forcing an out of bound appointment to test forc dropping
		body_start_at = self.faker.date_time_between(start_date=timeslot.start_at, end_date=appointment.start_at)
		body_end_at = self.faker.date_time_between(start_date=body_start_at, end_date=appointment.start_at)
		
		# mock request
		body = {
			'start_at': body_start_at.time(),
			'end_at': body_end_at.time(),
			'force_drop': True
		}

		request = auth_request(APIRequestFactory().put, f'timeslots/{timeslot.id}/', user=therapists.user, body=body)
		response = self.update(request, pk=timeslot.id)

		

		self.assertEqual(response.status_code, 200)
		self.assertTrue(AvailabilityTimeSlot.objects.filter(id=timeslot.id, start_at__time=body['start_at'], end_at__time=body['end_at'], group=None).exists())
		self.assertTrue(Appointment.objects.filter(id=appointment.id, timeslot=None, status=PENDING_THERAPIST).exists())
		self.assertTrue(TherapistAssignment.objects.filter(id=assignment.id, status=INACTIVE).exists())

	@tag('update-invalid-out-of-bound')
	def test_invalid_update_bounds(self):
		
		# mock therapist
		therapists = TherapistMock.mock_instances(n=1)[0]
		# mock timeslots
		group = AvailabilityTimeSlotGroup.objects.create()
		timeslot = AvailabilityTimeSlot.objects.create(
			therapist=therapists,
			start_at=timezone.now().replace(hour=0, minute=0, second=0),
			end_at=timezone.now().replace(hour=0, minute=0, second=0) + timedelta(hours=4),
			group=group

		)
		# link mocked appointment
		apptmnt_start_at = self.faker.date_time_between(start_date=timeslot.start_at, end_date=timeslot.end_at)
		apptmnt_end_at = self.faker.date_time_between(start_date=apptmnt_start_at, end_date=timeslot.end_at)
		appointment = Appointment.objects.create(
			patient=PatientMock.mock_instances(n=1)[0],
			timeslot=timeslot,
			start_at= apptmnt_start_at,
			end_at = apptmnt_end_at,
			)
		
		assignment = TherapistAssignment.objects.create(
			therapist_timeslot=timeslot,
			appointment=appointment,
			status=ACTIVE
		)

		# forcing an out of bound appointment to test forc dropping
		body_start_at = self.faker.date_time_between(start_date=timeslot.start_at, end_date=appointment.start_at)
		body_end_at = self.faker.date_time_between(start_date=body_start_at, end_date=appointment.start_at)
		
		# mock request
		body = {
			'start_at': body_start_at.time(),
			'end_at': body_end_at.time(),
			'force_drop': False
		}

		request = auth_request(APIRequestFactory().put, f'timeslots/{timeslot.id}/', user=therapists.user, body=body)
		response = self.update(request, pk=timeslot.id)

		

		self.assertEqual(response.status_code, 400)

	@tag('update-invalid-conflicts')
	def test_invalid_update_timeslot_conflict(self):
		
		# mock therapist
		therapists = TherapistMock.mock_instances(n=1)[0]
		# create an existing conflicting timeslot
		group = AvailabilityTimeSlotGroup.objects.create()
		first_timeslot = timezone.now().replace(hour=4, minute=0, second=0)
		conflicting_timeslot = AvailabilityTimeSlot.objects.create(
			therapist=therapists,
			start_at=first_timeslot,
			end_at=first_timeslot + timedelta(hours=2),
			group=group
		)

		# mock another timeslot to be updated
		group = AvailabilityTimeSlotGroup.objects.create()
		timeslot = AvailabilityTimeSlot.objects.create(
			therapist=therapists,
			start_at=timezone.now().replace(hour=0, minute=0, second=0),
			end_at=timezone.now().replace(hour=0, minute=0, second=0) + timedelta(hours=1),
			group=group

		)

		# mock the request
		body = {
			'start_at': conflicting_timeslot.start_at.time(),
			'end_at': (conflicting_timeslot.start_at + timedelta(minutes=30)).time()
		}

		request = auth_request(APIRequestFactory().put, f'timeslots/{timeslot.id}/', user=therapists.user, body=body)
		response = self.update(request, pk=timeslot.id)

		

		self.assertEqual(response.status_code, 400)

	
	@tag('batch-update-valid')
	def test_valid_batch_update(self):
		
		# mock a therapist
		therapist = TherapistMock.mock_instances(n=1)[0]
		# create a new batch of timeslots using API

		sunday: datetime = rrule.rrule(rrule.WEEKLY, dtstart=timezone.now(), byweekday=rrule.SU, count=1)[0]
		start_at= sunday.replace(hour=0, minute=0, second=0)
		end_at = start_at + timedelta(days=14)

		# mock request
		body = {
				'start_at': start_at,
				'end_at': end_at,
				'weekly_schedule': {
				
				'sunday': [
				{
					'start_at': timezone.now().replace(hour=1, second=0, minute=0).time(),
					'end_at': (timezone.now().replace(hour=1, second=0, minute=0) + timedelta(minutes=30)).time()
				}, {
					'start_at': (timezone.now().replace(hour=1, second=0, minute=0) + timedelta(hours=1)).time(),
					'end_at': (timezone.now().replace(hour=1, second=0, minute=0) + timedelta(hours=2)).time()
				}
			], 
			'monday': [
				{
					'start_at': timezone.now().replace(hour=1, second=0, minute=0).replace().time(),
					'end_at': (timezone.now().replace(hour=1, second=0, minute=0) + timedelta(hours=1)).time()
				}, {
					'start_at': (timezone.now().replace(hour=1, second=0, minute=0) + timedelta(hours=5)).time(),
					'end_at': (timezone.now().replace(hour=1, second=0, minute=0) + timedelta(hours=6)).time()
				}
			]
			
			}
			}
		
		request = auth_request(APIRequestFactory().post, f'timeslots/batch_create/', user=therapist.user, body=body)
		response = self.batch_create(request)


		self.assertEqual(response.status_code, 201)

		# fetching and batch updating the first timeslot on sunday
		timeslot = AvailabilityTimeSlot.objects.get(therapist=therapist, start_at=sunday.replace(hour=1, minute=0, second=0))

		# mock request
		body = {
			'start_at': (sunday.replace(hour=4, minute=0, second=0) + timedelta(hours=1)).time(),
			'end_at': (sunday.replace(hour=5, minute=0, second=0) + timedelta(hours=2)).time()
		}

		request = auth_request(APIRequestFactory().put, f'timeslots/{timeslot.pk}/batch_update/', user=therapist.user, body=body)
		response = self.batch_update(request, pk=timeslot.pk)

		
		self.assertEqual(response.status_code, 200)
		# checking that the update was performed correctly
		## refetching again because the timeslot group has been detached from original
		## upon updating it
		timeslot = AvailabilityTimeSlot.objects.get(pk=timeslot.pk)
		self.assertEqual(AvailabilityTimeSlot.objects.filter(group=timeslot.group, start_at__time=body['start_at'], end_at__time=body['end_at']).count(), 2)

	@tag('batch-update-valid-force-drop')
	def test_valid_batch_update_with_force_drop(self):

		# mock a therapist
		therapist = TherapistMock.mock_instances(n=1)[0]
		# create a new batch of timeslots using API

		sunday: datetime = rrule.rrule(rrule.WEEKLY, dtstart=timezone.now(), byweekday=rrule.SU, count=1)[0]
		start_at= sunday.replace(hour=0, minute=0, second=0)
		end_at = start_at + timedelta(days=14)

		# mock request
		body = {
				'start_at': start_at,
				'end_at': end_at,
				'weekly_schedule': {
				
				'sunday': [
				{
					'start_at': timezone.now().replace(hour=1, second=0, minute=0).time(),
					'end_at': (timezone.now().replace(hour=1, second=0, minute=0) + timedelta(minutes=30)).time()
				}, {
					'start_at': (timezone.now().replace(hour=1, second=0, minute=0) + timedelta(hours=1)).time(),
					'end_at': (timezone.now().replace(hour=1, second=0, minute=0) + timedelta(hours=2)).time()
				}
			], 
			'monday': [
				{
					'start_at': timezone.now().replace(hour=1, second=0, minute=0).replace().time(),
					'end_at': (timezone.now().replace(hour=1, second=0, minute=0) + timedelta(hours=1)).time()
				}, {
					'start_at': (timezone.now().replace(hour=1, second=0, minute=0) + timedelta(hours=5)).time(),
					'end_at': (timezone.now().replace(hour=1, second=0, minute=0) + timedelta(hours=6)).time()
				}
			]
			
			}
			}
		
		request = auth_request(APIRequestFactory().post, f'timeslots/batch_create/', user=therapist.user, body=body)
		response = self.batch_create(request)


		self.assertEqual(response.status_code, 201)

		# fetching and batch updating the first timeslot on sunday
		timeslot = AvailabilityTimeSlot.objects.get(therapist=therapist, start_at=sunday.replace(hour=1, minute=0, second=0))

		# create an apppointment that will fall out of the updated timeslot time range
		apptmnt_start_at = self.faker.date_time_between(start_date=timeslot.start_at, end_date=timeslot.end_at)
		apptmnt_end_at = self.faker.date_time_between(start_date=apptmnt_start_at, end_date=timeslot.end_at)

		appointment = Appointment.objects.create(
			patient=PatientMock.mock_instances(n=1)[0],
			timeslot=timeslot,
			start_at= apptmnt_start_at,
			end_at = apptmnt_end_at
		)
		# creating a therapist assignment to test assignment dropping
		TherapistAssignment.objects.create(
			therapist_timeslot=timeslot,
			appointment=appointment,
			status=ACTIVE
		)


		# mock request
		body = {
			'start_at': (sunday.replace(hour=4, minute=0, second=0) + timedelta(hours=1)).time(),
			'end_at': (sunday.replace(hour=5, minute=0, second=0) + timedelta(hours=2)).time(),
			'force_drop': True
		}

		request = auth_request(APIRequestFactory().put, f'timeslots/{timeslot.pk}/batch_update/', user=therapist.user, body=body)
		response = self.batch_update(request, pk=timeslot.pk)

		
		self.assertEqual(response.status_code, 200)
		# checking that the update was performed correctly
		## refetching again because the timeslot group has been detached from original
		## upon updating it
		timeslot = AvailabilityTimeSlot.objects.get(pk=timeslot.pk)
		self.assertEqual(AvailabilityTimeSlot.objects.filter(group=timeslot.group, start_at__time=body['start_at'], end_at__time=body['end_at']).count(), 2)

		

	@tag('batch-update-invalid-conflict')
	def test_invalid_update_conflict(self):
		
		# mock a therapist
		therapist = TherapistMock.mock_instances(n=1)[0]
		# create a new batch of timeslots using API

		sunday: datetime = rrule.rrule(rrule.WEEKLY, dtstart=timezone.now(), byweekday=rrule.SU, count=1)[0]
		start_at= sunday.replace(hour=0, minute=0, second=0)
		end_at = start_at + timedelta(days=14)

		# mock request
		body = {
				'start_at': start_at,
				'end_at': end_at,
				'weekly_schedule': {
				
				'sunday': [
				{
					'start_at': timezone.now().replace(hour=1, second=0, minute=0).time(),
					'end_at': (timezone.now().replace(hour=1, second=0, minute=0) + timedelta(minutes=30)).time()
				}, {
					'start_at': (timezone.now().replace(hour=1, second=0, minute=0) + timedelta(hours=1)).time(),
					'end_at': (timezone.now().replace(hour=1, second=0, minute=0) + timedelta(hours=2)).time()
				}
			], 
			'monday': [
				{
					'start_at': timezone.now().replace(hour=1, second=0, minute=0).replace().time(),
					'end_at': (timezone.now().replace(hour=1, second=0, minute=0) + timedelta(hours=1)).time()
				}, {
					'start_at': (timezone.now().replace(hour=1, second=0, minute=0) + timedelta(hours=5)).time(),
					'end_at': (timezone.now().replace(hour=1, second=0, minute=0) + timedelta(hours=6)).time()
				}
			]
			
			}
			}
		
		request = auth_request(APIRequestFactory().post, f'timeslots/batch_create/', user=therapist.user, body=body)
		response = self.batch_create(request)


		self.assertEqual(response.status_code, 201)

		# fetching and batch updating the first timeslot on sunday
		timeslot = AvailabilityTimeSlot.objects.get(therapist=therapist, start_at=sunday.replace(hour=1, minute=0, second=0))


		# mock request
		body = {
			'start_at': (sunday.replace(hour=1, minute=0, second=0) + timedelta(hours=1)).time(),
			'end_at': (sunday.replace(hour=1, minute=0, second=0) + timedelta(hours=2)).time(),
		}

		request = auth_request(APIRequestFactory().put, f'timeslots/{timeslot.pk}/batch_update/', user=therapist.user, body=body)
		response = self.batch_update(request, pk=timeslot.pk)

		
		self.assertEqual(response.status_code, 400)
		# checking that the update was performed correctly
		## refetching again because the timeslot group has been detached from original
		## upon updating it
		timeslot = AvailabilityTimeSlot.objects.get(pk=timeslot.pk)
		self.assertEqual(AvailabilityTimeSlot.objects.filter(pk=timeslot.pk, start_at__time=body['start_at'], end_at__time=body['end_at']).count(), 0)


	@tag('destroy-valid')
	def test_valid_destroy(self):
		
		# mock therapist
		therapists = TherapistMock.mock_instances(n=1)[0]
		# mock timeslots
		timeslot = AvailabilityTimeslotMocker.mock_instances(n=1, fixed_therapist=therapists)[0]
		# mock request
		request = auth_request(APIRequestFactory().delete, f'timeslots/{timeslot.id}/', user=therapists.user)
		response = self.destroy(request, pk=timeslot.id)

		self.assertEqual(response.status_code, 200)
		self.assertFalse(AvailabilityTimeSlot.objects.filter(id=timeslot.id, active=True).exists())

	@tag('destroy-valid-force-drop')
	def test_valid_destroy_force_drop(self):
			
			# mock therapist
			therapists = TherapistMock.mock_instances(n=1)[0]
			# mock timeslots
			timeslot = AvailabilityTimeslotMocker.mock_instances(n=1, fixed_therapist=therapists)[0]
			# mock appointment
			appointment = Appointment.objects.create(
				patient=PatientMock.mock_instances(n=1)[0],
				timeslot=timeslot,
				start_at= timeslot.start_at,
				end_at= timeslot.end_at
			)
			# mock assignment
			assignment = TherapistAssignment.objects.create(
				therapist_timeslot=timeslot,
				appointment=appointment,
				status=ACTIVE
			)
			# mock request
			request = auth_request(APIRequestFactory().delete, f'timeslots/{timeslot.id}/', user=therapists.user, body={'force_drop': True})
			response = self.destroy(request, pk=timeslot.id)

			
	
			self.assertEqual(response.status_code, 200)
			self.assertFalse(AvailabilityTimeSlot.objects.filter(id=timeslot.id, active=True).exists())
			self.assertTrue(Appointment.objects.filter(id=appointment.id, timeslot=None, status=PENDING_THERAPIST).exists())
			self.assertTrue(TherapistAssignment.objects.filter(appointment=appointment, status=INACTIVE).exists())

	@tag('destroy-invalid-therapist')
	def test_invalid_destroy_therapist(self):
		
		# mock therapist
		therapists = TherapistMock.mock_instances(n=2)
		# mock timeslots
		timeslot = AvailabilityTimeslotMocker.mock_instances(n=1, fixed_therapist=therapists[0])[0]
		# mock request
		request = auth_request(APIRequestFactory().delete, f'timeslots/{timeslot.id}/', user=therapists[1].user)
		response = self.destroy(request, pk=timeslot.id)

		self.assertEqual(response.status_code, 404)

	@tag('destroy-invalid-conflict')
	def test_invalid_destroy_conflict(self):
		
		# mock therapist
		therapist = TherapistMock.mock_instances(n=1)[0]
		# mock timeslots
		timeslot = AvailabilityTimeslotMocker.mock_instances(n=1, fixed_therapist=therapist)[0]
		# mock appointment
		appointment = Appointment.objects.create(
			patient=PatientMock.mock_instances(n=1)[0],
			timeslot=timeslot,
			start_at= timeslot.start_at,
			end_at= timeslot.end_at
		)
		# mock request
		request = auth_request(APIRequestFactory().delete, f'timeslots/{timeslot.id}/', user=therapist.user)
		response = self.destroy(request, pk=timeslot.id)

		self.assertEqual(response.status_code, 400)
		self.assertTrue(AvailabilityTimeSlot.objects.filter(id=timeslot.id).exists())

	@tag('destroy-invalid-patient')
	def test_invalid_destroy_patient(self):
		
		# mock therapist
		therapists = TherapistMock.mock_instances(n=1)[0]
		# mock timeslots
		timeslot = AvailabilityTimeslotMocker.mock_instances(n=1, fixed_therapist=therapists)[0]
		# mock request
		request = auth_request(APIRequestFactory().delete, f'timeslots/{timeslot.id}/', user=PatientMock.mock_instances(n=1)[0].user)
		response = self.destroy(request, pk=timeslot.id)

		self.assertEqual(response.status_code, 403)
	