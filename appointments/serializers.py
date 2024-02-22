
from os import write
from click import group
from rest_framework import serializers
from appointments.constants.enums import ACCEPTED, CONFIRMED, INACTIVE, PENDING, PENDING_THERAPIST, REJECTED, WEEK_DAYS
from appointments.models import Appointment, PatientReferralRequest
from authentication.serializers import UserReadSerializer
from core.http import ValidationError
from core.serializers import HttpErrorSerializer, HttpSuccessResponeSerializer
from rest_framework import serializers
from appointments.constants.enums import ACTIVE
from appointments.models import Appointment, AvailabilityTimeSlot, TherapistAssignment
from core.http import ValidationError
from django.utils import timezone
from core.serializers import  HttpSuccessResponeSerializer
from django.db.models import Q, F
from django.utils import timezone
from rest_framework import serializers
from appointments.models import AvailabilityTimeSlot, AvailabilityTimeSlotGroup
from authentication.serializers import TherapistReadSerializer
from core.http import ValidationError
from core.models import Therapist
from core.serializers import HttpErrorResponseSerializer, HttpSuccessResponeSerializer, HttpPaginatedSerializer
from django.db.models import Q
from core.types import DatetimeInterval
from core.utils.time import TimeUtil
from django.db.models.functions import ExtractHour, ExtractMinute, ExtractWeekDay
from django.utils.translation import gettext as _
from datetime import datetime
from rest_framework.exceptions import ValidationError as VE
from drf_yasg.utils import swagger_serializer_method

class ReferralRequestReadSerializer(serializers.ModelSerializer):
	"""Serializer for listing referral requests"""

	responding_therapist = serializers.SerializerMethodField()
	referee = UserReadSerializer()
	referrer = UserReadSerializer()
	
	def get_responding_therapist(self, instance: PatientReferralRequest):
		return UserReadSerializer(instance=instance.responding_therapist.user).data
	class Meta:
		model = PatientReferralRequest
		fields = ['id', 'referrer', 'referee', 'reason', 'status', 'responding_therapist', 'appointment']
		depth = 1

class HttpReferralRequestListSerializer(HttpSuccessResponeSerializer):
	"""Serializer for listing referral requests"""
	data = ReferralRequestReadSerializer(many=True)

class HttpReferralRequestRetrieveSerializer(HttpSuccessResponeSerializer):
	"""Serializer for listing referral requests"""
	data = ReferralRequestReadSerializer()


class ReferralRequestCreateSerializer(serializers.ModelSerializer):
	"""Serializer for creating referral requests"""

	def validate(self, attrs):
		
		referrer = self.context['request'].user
		if PatientReferralRequest.objects.filter(referrer=referrer, referee=attrs['referee'], status=PENDING).exists():
			raise ValidationError(_('A referral request already exists for this referee'))

		if not hasattr(attrs['referee'], 'patient_profile'):
			raise ValidationError(_('The referee is not a patient'))
		
		if referrer.pk  == attrs['referee']:
			raise ValidationError(_('You cannot refer yourself. create an appointment'))

		return attrs 
	class Meta:
		model = PatientReferralRequest
		fields = [ 'referee', 'reason', 'id']

	def create(self, validated_data):
		validated_data['status'] = PENDING
		validated_data['referrer'] = self.context['request'].user
		
		return super().create(validated_data)

class HttpReferralRequestCreateResponseSerializer(HttpSuccessResponeSerializer):
	"""Serializer for creating referral requests"""
	data = ReferralRequestCreateSerializer()

class ReferralRequestCreateErrorInnerWrapperSerializer(serializers.Serializer):
	"""Serializer used for Signup credential validation on data level"""
	referee = serializers.ListSerializer(child=serializers.CharField(allow_blank=True, max_length=150))
	reason = serializers.ListSerializer(child=serializers.CharField(allow_blank=True, max_length=128))
	error = serializers.ListSerializer(child=serializers.CharField(allow_blank=True, max_length=128))

class ReferralRequestCreateErrorOuterWrapperSerializer(serializers.Serializer):
	errors = ReferralRequestCreateErrorInnerWrapperSerializer()

class HttpErrReferralRequestCreateSerializer(HttpErrorResponseSerializer):
	"""Serializer used for swagger HTTP schema"""
	data = ReferralRequestCreateErrorOuterWrapperSerializer()


class ReferralRequestUpdateSerializer(serializers.ModelSerializer):

	def validate(self, attrs):
		
		referrer = self.context['request'].user
		if not PatientReferralRequest.objects.filter(pk=self.instance.pk, status=PENDING).exists():
			raise ValidationError(_('Referral request is not pending'))
		
		if not hasattr(attrs['referee'], 'patient_profile'):
			raise ValidationError(_('The referee is not a patient'))
		
		if referrer.pk  == attrs['referee']:
			raise ValidationError(_('You cannot refer yourself. create an appointment'))

		return attrs

	class Meta:
		model = PatientReferralRequest
		fields = ['referee', 'reason']


class HttpSuccessReferralRequestUpdateResponseSerializer(HttpSuccessResponeSerializer):
	"""Serializer for updating referral requests"""
	data = ReferralRequestUpdateSerializer()

class ReferralUpdateInnerErrorWrapper(serializers.Serializer):
	referee = serializers.ListSerializer(child=serializers.CharField(), allow_null=True)
	reason = serializers.ListSerializer(child=serializers.CharField(), allow_null=True)
	error = serializers.ListSerializer(child=serializers.CharField(), allow_null=True)

class ReferralUpdateOuterErrorWrapper(serializers.Serializer):
	errors = ReferralUpdateInnerErrorWrapper()

class HttpErroReferralRequestUpdateSerializer(HttpErrorResponseSerializer):
	data = ReferralUpdateOuterErrorWrapper()

class ReferralRequestReplySerializer(serializers.ModelSerializer):

	status = serializers.ChoiceField(choices=[ACCEPTED, REJECTED])

	class Meta:
		model = PatientReferralRequest
		fields = ['status']

	def update(self, instance: PatientReferralRequest, validated_data):

		# create an appointment if the status is accepted
		if validated_data['status'] == ACCEPTED:
			# TODO: find a way to handle duplicate active appointments
			appointment = Appointment.objects.create(patient=instance.referee.patient_profile, status=PENDING_THERAPIST)
			validated_data['appointment'] = appointment

		return super().update(instance, validated_data)
	

class HttpReferralRequestReplyResponseSerializer(HttpSuccessResponeSerializer):
	"""Serializer for updating referral requests"""
	data = ReferralRequestReplySerializer()

class ReferralRequestReplyErrorInnerWrapperSerializer(serializers.Serializer):
	"""Serializer used for Signup credential validation on data level"""
	status = serializers.ListSerializer(child=serializers.CharField(allow_blank=True, max_length=150), allow_null=True)
	error = serializers.ListSerializer(child=serializers.CharField(allow_blank=True, max_length=128), allow_null=True)

class ReferralRequestReplyErrorOuterWrapperSerializer(serializers.Serializer):
	errors = ReferralRequestReplyErrorInnerWrapperSerializer()

class HttpErrReferralRequestReplySerializer(HttpErrorResponseSerializer):
	"""Serializer used for swagger HTTP schema"""
	data = ReferralRequestReplyErrorOuterWrapperSerializer()

class RawAvailabilityTimeslotReadSerializer(serializers.ModelSerializer):
	"""Serializer for listing availability timeslots"""
	therapist = serializers.SerializerMethodField()

	def get_therapist(self, instance):

		return TherapistReadSerializer(instance=instance.therapist.user).data
	
	class Meta:
		model = AvailabilityTimeSlot
		fields = ['id', 'therapist', 'start_at', 'end_at', 'created_at']

class RawAppointmentReadSerializer(serializers.ModelSerializer):
	"""Serializer for listing appointments"""
	

	class Meta:
		model = Appointment
		fields = ['id', 'status', 'start_at', 'end_at']

class AvailabilityTimeslotReadSerializer(serializers.ModelSerializer):
	"""Serializer for listing availability timeslots"""
	therapist = serializers.SerializerMethodField()

	linked_appointments = serializers.SerializerMethodField()

	@swagger_serializer_method(serializer_or_field=RawAppointmentReadSerializer)
	def get_linked_appointments(self, instance):
		return RawAppointmentReadSerializer(instance=instance.linked_appointments, many=True).data

	@swagger_serializer_method(serializer_or_field=TherapistReadSerializer)
	def get_therapist(self, instance):

		return TherapistReadSerializer(instance=instance.therapist.user).data
	
	class Meta:
		model = AvailabilityTimeSlot
		fields = ['id', 'therapist', 'linked_appointments',  'start_at', 'end_at', 'created_at']

class HttpPaginatedAvailabilityTimeslotListSerializer(HttpPaginatedSerializer):
	"""Serializer for listing availability timeslots"""
	results = AvailabilityTimeslotReadSerializer(many=True)

class HttpAvailabilityTimeslotListSerializer(HttpSuccessResponeSerializer):
	"""Serializer for listing availability timeslots"""
	data = HttpPaginatedAvailabilityTimeslotListSerializer()    

class HttpAvailabilityTimeslotRetrieveSerializer(HttpSuccessResponeSerializer):
	"""Serializer for listing availability timeslots"""
	data = AvailabilityTimeslotReadSerializer()


class DatetimeIntervalSerializer(serializers.Serializer):
	"""Serializer for specifying time intervals"""
	start_at = serializers.DateTimeField()
	end_at = serializers.DateTimeField()

	def validate(self, attrs):

		if attrs.get('start_at') >= attrs.get('end_at'):
			raise ValidationError(_('Start time must be less than end time'))

		return attrs

class TimeIntervalSerializer(serializers.Serializer):
	"""Serializer for specifying time intervals"""
	start_at = serializers.TimeField()
	end_at = serializers.TimeField()

	def validate(self, attrs):

		if attrs.get('start_at') >= attrs.get('end_at'):
			raise ValidationError(_('Start time must be less than end time'))

		return attrs

class FutureDatetimeIntervalSerializer(DatetimeIntervalSerializer):

	def validate(self, attrs):

		if attrs.get('start_at') < timezone.now():
			raise ValidationError(_('Start time must be in the future'))

		return super().validate(attrs)


class TimeonlyWeekRepresentationSerializer(serializers.Serializer):

	sunday = TimeIntervalSerializer(many=True, allow_null=True, required=False)
	monday = TimeIntervalSerializer(many=True,  allow_null=True, required=False)
	tuesday = TimeIntervalSerializer(many=True,  allow_null=True, required=False)
	wednesday = TimeIntervalSerializer(many=True,  allow_null=True, required=False)
	thursday = TimeIntervalSerializer(many=True,  allow_null=True, required=False)

	def validate(self, attrs):

		if not any([attrs.get('sunday'), attrs.get('monday'), attrs.get('tuesday'), attrs.get('wednesday'), attrs.get('thursday')]):
			raise ValidationError('At least one day must be selected')

		return attrs

class DateTimeWeeklyRepresentationSerializer(serializers.Serializer):
	
		sunday = DatetimeIntervalSerializer(many=True, allow_null=True, required=False)
		monday = DatetimeIntervalSerializer(many=True,  allow_null=True, required=False)
		tuesday = DatetimeIntervalSerializer(many=True,  allow_null=True, required=False)
		wednesday = DatetimeIntervalSerializer(many=True,  allow_null=True, required=False)
		thursday = DatetimeIntervalSerializer(many=True,  allow_null=True, required=False)
	
		def validate(self, attrs):
			
			if not any([attrs.get('sunday'), attrs.get('monday'), attrs.get('tuesday'), attrs.get('wednesday'), attrs.get('thursday')]):
				raise ValidationError('At least one day must be selected')
	
			return attrs


class AvailabilityTimeslotCreateSerializer(serializers.Serializer):
	"""
		Serializer to create availabiltiy timslots for a single week only
	"""
	
	intervals = DatetimeIntervalSerializer(many=True, allow_null=False, required=True)


	def validate(self, attrs):
		"""
		Collecting all possible interval conflict errors and raise at once
		to avoid user frustration
		"""
		intervals = attrs['intervals']
		sorted_intervals = sorted(intervals, key=lambda interval: interval['start_at'], reverse=False)

		is_conflicting, uploaded_timeslot_conflict_pairs= TimeUtil.check_sequential_conflicts([ DatetimeInterval(**interval) for interval in sorted_intervals], sort=False)

		if is_conflicting:
			raise ValidationError(message=_('The following intervals conflict with each other: '), data={
				'uploaded_timeslot_conflict_pairs': uploaded_timeslot_conflict_pairs
			})

		# getting all possible conflicting timeslots to avoid fetching each record in a loop
		possible_conflicting_timeslots = AvailabilityTimeSlot.objects.filter(
			Q(active=True) &
			Q(therapist= Therapist.objects.get(user=self.context['request'].user)) & 
			Q(start_at__lte=sorted_intervals[0]['end_at'], end_at__gte=sorted_intervals[0]['start_at']) 
		)

		
		existing_timeslot_conflicts =[]

		# checking for conflicts between uploaded intervals and existing intervals
		for interval in sorted_intervals:
			conflicting_intervals = possible_conflicting_timeslots.filter(
				Q(start_at__lte=interval['end_at'], end_at__gte=interval['start_at'])
			)
			# if there exists existing intervals that are conflict supply the uploaded interval, and all existing conflicting intervals
			if conflicting_intervals.exists():
				existing_timeslot_conflicts.append({
					'interval': interval,
					'conflicting_timeslots': AvailabilityTimeslotReadSerializer(instance=conflicting_intervals, many=True).data
				
				})

		if len(existing_timeslot_conflicts) > 0:
			raise ValidationError(message=_('The following intervals conflict with existing timeslots: '), data={
				'existing_timeslot_conflicts': existing_timeslot_conflicts,
			})

		return attrs

	def create(self, validated_data):

		group = AvailabilityTimeSlotGroup.objects.create()
		
		for interval in validated_data['intervals']:
			AvailabilityTimeSlot.objects.create(
				therapist= Therapist.objects.get(user=self.context['request'].user),
				start_at=interval['start_at'],
				end_at=interval['end_at'],
				group=group
			)

		return validated_data

class AvailabilityTimeslotBatchUploadSerializer(FutureDatetimeIntervalSerializer):
	"""
		Serializer used to validate the updloaded absolute time-based weekly schedule
	"""
	weekly_schedule = TimeonlyWeekRepresentationSerializer(allow_null=False)
	
class AvailabilityTimeslotBatchCreateSerializer(FutureDatetimeIntervalSerializer):
	"""
		Serializer used to validate the generated absolute datetime intervals
		for each day of the week
	"""

	weekly_schedule = DateTimeWeeklyRepresentationSerializer(allow_null=False)

	def validate(self, attrs):
		
		possible_conflicting_timeslots = AvailabilityTimeSlot.objects.filter(
			Q(therapist= Therapist.objects.get(user=self.context['request'].user)) & 
			Q(start_at__lte=attrs['end_at'], end_at__gte=attrs['start_at'])
			)
		# setting up an error collection object for precise error reporting
		error_obj = {
			'sunday': {
				'uploaded_conflicts': [],
				'existing_conflicts': []
			},
			'monday': {
				'uploaded_conflicts': [],
				'existing_conflicts': []
			},
			'tuesday': {
				'uploaded_conflicts': [],
				'existing_conflicts': []
			},
			'wednesday': {
				'uploaded_conflicts': [],
				'existing_conflicts': []
			},
			'thursday': {
				'uploaded_conflicts': [],
				'existing_conflicts': []
			}
		}
		for day in error_obj.keys():
			intervals = attrs['weekly_schedule'][day]
			sorted_intervals = sorted(intervals, key=lambda interval: interval['start_at'], reverse=False)
			
			# 1. checking for conflict between uploaded intervals for each day
			is_conflicting, uploaded_timeslot_conflict_pairs= TimeUtil.check_sequential_conflicts([ DatetimeInterval(**interval) for interval in sorted_intervals], sort=False)
			error_obj[day]['uploaded_conflicts'] = uploaded_timeslot_conflict_pairs

			# 2. checking for exisitng conflicting timeslots with uploaded intervals   
			for interval in sorted_intervals:
				conflicting_intervals = possible_conflicting_timeslots.filter(
				Q(start_at__lte=interval['end_at'], end_at__gte=interval['start_at'])
				)
				
				if conflicting_intervals.exists():
					error_obj[day]['existing_conflicts'].append({
						'interval': interval,
						'conflicting_timeslots': AvailabilityTimeslotReadSerializer(instance=conflicting_intervals, many=True).data
					})
				
		if any([len(error_obj[day]['uploaded_conflicts']) > 0 or len(error_obj[day]['existing_conflicts']) > 0 for day in error_obj.keys()]):
			raise ValidationError(message=_('The following intervals conflict with existing timeslots: '), data=error_obj)


		return attrs

	def create(self, validated_data):
		"""
			Creating all approved timeslots under the jurisdiction of the performing therapist
		"""

		timeslots = []
		timeslot_group = AvailabilityTimeSlotGroup.objects.create()
		therapist = Therapist.objects.get(user=self.context['request'].user)

		for day in validated_data['weekly_schedule'].keys():
			for interval in validated_data['weekly_schedule'][day]:
				timeslots.append(
					AvailabilityTimeSlot(
						therapist= therapist,
						start_at=interval['start_at'],
						end_at=interval['end_at'],
						group=timeslot_group
					)
				)
		
		AvailabilityTimeSlot.objects.bulk_create(timeslots)
		
		return validated_data
	

# --------------- Swagger formatting serializers ------------

class HttpAvailabilityTimeslotCreateResponseSerializer(serializers.Serializer):

	data = AvailabilityTimeslotCreateSerializer()

class SingleTimeslotErrorSerializer(serializers.Serializer):
	interval = DatetimeIntervalSerializer()
	conflicting_timeslots = AvailabilityTimeslotReadSerializer(many=True)
	
class SingleCreateErrorContentSerializer(serializers.Serializer):
	existing_timeslot_conflicts = DatetimeIntervalSerializer(many=True, allow_null=True)
	uploaded_timeslot_conflict_pairs = serializers.ListSerializer(child= SingleTimeslotErrorSerializer(), allow_null=True)

class BatchCreateErrorContentSerializer(serializers.Serializer):
	uploaded_timeslot_conflict_pairs = serializers.ListSerializer(child= SingleTimeslotErrorSerializer(), allow_null=True)

class CreateErrorInnerWrapperSerializer(serializers.Serializer):
  
	data = SingleCreateErrorContentSerializer()

class BatchCreateErrorInnerWrapperSerializer(serializers.Serializer):
	
	sunday = SingleCreateErrorContentSerializer(allow_null=True)
	monday = SingleCreateErrorContentSerializer(allow_null=True)
	tuesday = SingleCreateErrorContentSerializer(allow_null=True)
	wednesday = SingleCreateErrorContentSerializer(allow_null=True)
	thursday = SingleCreateErrorContentSerializer(allow_null=True)

class CreateErrorOuterWrapperSerializer(serializers.Serializer):
	data = BatchCreateErrorInnerWrapperSerializer()
	error = serializers.ListSerializer(child=serializers.CharField())

class HttpCreateTimeslotRawErrorSerializer(serializers.Serializer):
	errors = CreateErrorOuterWrapperSerializer()

class BatchCreateFinalWrapperSerializer(serializers.Serializer):
	errors = BatchCreateErrorInnerWrapperSerializer()


class HttpErrorAvailabilityTimeslotBatchCreateResponse(HttpErrorResponseSerializer):
	data = HttpCreateTimeslotRawErrorSerializer()
	
class AvailabilityTimeslotBatchUpdateSerializer(TimeIntervalSerializer):
	"""
		Serializer to only update the successive timeslots IN ONE TIME INTERVAL
		WITHIN THE TIMESLOT GROUP
	"""
	force_drop = serializers.BooleanField(default=False)

	def validate(self, value):


		# checking if the timeslot is in the past
		if self.instance.start_at < timezone.now():
			raise ValidationError(_('Cannot update past timeslots'))

		# 1. checking for conflict with other timeslots by the same therapist

		self.affected_slots = AvailabilityTimeSlot.objects\
		.annotate(weekday= ExtractWeekDay('start_at')).filter(
			Q(therapist=self.context['request'].user.therapist_profile) &
			# getting all timeslots that occur in the same weekday, and time range
			# after the selected timeslot to update
			Q(weekday=(self.instance.start_at.weekday() + 2) % 7) &
			Q(start_at__time=self.instance.start_at, end_at__time=self.instance.end_at) &
			Q(start_at__date__gte=self.instance.start_at.date()) &
			Q(group=self.instance.group)
			)	
		
		# specifying the full boundary of effect
		first_date = self.affected_slots.earliest('start_at').start_at.date()
		last_date = self.affected_slots.latest('end_at').end_at.date()

		# for partial updating, we need to get the missing start and end times from the instance
		start_at = value['start_at'] or self.instance.start_at.time()
		end_at = value['end_at'] or self.instance.end_at.time()

		conflicting_timeslots = AvailabilityTimeSlot.objects.annotate(
			weekday= ExtractWeekDay('start_at'),
		).filter(
			# getting all appointments by this therapist
			# that occur in same weekday, and date range
			# having a conflicting time range with the updated
			# time range (start_at, end_at)  
			Q(therapist= Therapist.objects.get(user=self.context['request'].user)) &
			Q(weekday=(self.instance.start_at.weekday() + 2) % 7
			,start_at__time__lte=end_at, end_at__time__gte=start_at, 
	 		start_at__date__gte=first_date, end_at__date__lte=last_date)
			)
		
		if conflicting_timeslots.exists():
			raise ValidationError(message=_('The following timeslots conflict with new updated timeslots: '), data={
				'conflicting_timeslots': AvailabilityTimeslotReadSerializer(instance=conflicting_timeslots, many=True).data
			})
		
		# 2. checking that no appointment linked to this timeslot fall out of the new interval, if force drop is not true
		if not value.get('force_drop', False):
			appointments = Appointment.objects.annotate(
				weekday= ExtractWeekDay('start_at'),
			).filter(
				Q(timeslot__group=self.instance.group) &
				Q(weekday=(self.instance.start_at.weekday() + 2) % 7) &
				(Q(start_at__time__lt=start_at) | Q(end_at__time__gt=end_at))
			)

			# TODO: include in error object
			if appointments.exists():
				raise ValidationError(message=_('The following appointments fall out of the new interval: '), data={
					'dropped_appointments': AppointmentReadSerializer(instance=appointments, many=True).data
				})
		
		return value



	def update(self, instance, validated_data):
		
		start_at = validated_data['start_at'] or self.instance.start_at.time()
		end_at = validated_data['end_at'] or self.instance.end_at.time()
		# drop any appointments outside the boundaries of new intervals
		if validated_data.get('force_drop', False):
			dropped_appointments = Appointment.objects.annotate(weekday = ExtractWeekDay('start_at')).filter(
				Q(timeslot__group=instance.group) &
				Q(weekday=(instance.start_at.weekday() + 2) % 7) &
				# filtering appointments that were originally inside timeslot and now outside
				(Q(start_at__time__lt=start_at) | Q(end_at__time__gt=end_at))
			)

			
			# DO NOT REMOVE THE LIST OPERATOR OR CHANGE ORDER OF THESE 2 LINES TO MAINTAIN WORLD PEACE 
			affected_ids = list(dropped_appointments.values_list('id', flat=True))
		
			affected = dropped_appointments.update(timeslot=None, status=PENDING_THERAPIST)

			affected_assignments = TherapistAssignment.objects.filter(appointment__pk__in= affected_ids).update(status=INACTIVE)

			
			


		# update the timeslot group of the updated timeslots
		
		# create a new availability timeslot group for the updated group of updated intervals
		group = AvailabilityTimeSlotGroup.objects.create()
		for timeslot in self.affected_slots:
			timeslot.group=group
			timeslot.start_at = datetime.combine(timeslot.start_at, start_at) 
			timeslot.end_at = datetime.combine(timeslot.end_at, end_at)

		updated = AvailabilityTimeSlot.objects.bulk_update(self.affected_slots, ['group', 'start_at', 'end_at'])

		

		return validated_data


class AvailabilityTimeslotSingleUpdateSerializer(TimeIntervalSerializer):
	"""
		Serializer for updating a single availability timeslot
	"""
	force_drop = serializers.BooleanField(default=False)


	def validate(self, attrs):

		start_at = self.instance.start_at.combine(self.instance.start_at.date(), attrs['start_at'] or self.instance.start_at.time())
		end_at = self.instance.end_at.combine(self.instance.end_at.date(), attrs['end_at'] or self.instance.end_at.time())

		# 1. checking for conflict with other timeslots by the same therapist
		conflicting_timeslots = AvailabilityTimeSlot.objects.filter(
			Q(therapist= Therapist.objects.get(user=self.context['request'].user)) &
			~Q(pk=self.instance.pk) & 
			Q(start_at__lte=end_at, end_at__gte=start_at) 
			)
		
		if self.instance.start_at < timezone.now():
			raise ValidationError(_('Cannot update past timeslots'))

		if conflicting_timeslots.exists():
			raise ValidationError(message=_('The following intervals conflict with existing timeslots: '), data={
				'interval': attrs,
				'conflicting_timeslots': AvailabilityTimeslotReadSerializer(instance=conflicting_timeslots, many=True).data
			})
		
		
		# 2. checking that no appointment linked to this timeslot fall out of the new interval, if froce drop is not true
		if not attrs.get('force_drop', False):
			appointments = self.instance.linked_appointments.filter(
				Q(start_at__lt=start_at) | Q(end_at__gt=end_at)
			)

			
			
			if appointments.exists():
				raise ValidationError(message=_('The following appointments fall out of the new interval: '), data={
					'dropped_appointments': AppointmentReadSerializer(instance=appointments, many=True).data
				})
			
		return attrs
		

	def update(self, instance, validated_data):

		
		start_at = self.instance.start_at.combine(self.instance.start_at.date(), validated_data['start_at'])
		end_at = self.instance.end_at.combine(self.instance.end_at.date(), validated_data['end_at'])

		# drop all appointments falling out of range when using force drop
		if validated_data.get('force_drop', False):
			dropped_appointments=instance.linked_appointments.filter(
				
				Q(start_at__lt=start_at) | Q(end_at__gt=end_at))

			# DO NOT REMOVE THE LIST OPERATOR TO MAINTAIN WORLD PEACE 
			affected_ids = list(dropped_appointments.values_list('id', flat=True))
		
			affected = dropped_appointments.update(timeslot=None, status=PENDING_THERAPIST)

			affected_assignments = TherapistAssignment.objects.filter(therapist_timeslot=self.instance, appointment__pk__in= affected_ids).update(status=INACTIVE)

			
			

		instance.start_at = start_at
		instance.end_at = end_at
		instance.group = None ## detaching the updated instnace from the timeslot group to avoid problems in batch editing
		instance.save()

		return validated_data


class UpdateErrorInnerWrapperSerializer(serializers.Serializer):
	conflicting_timeslots = AvailabilityTimeslotReadSerializer(many=True, allow_null=True)
	dropped_appointments = AvailabilityTimeslotReadSerializer(many=True, allow_null=True)

class UpdateErrorOuterWrapperSerializer(serializers.Serializer):
	data = UpdateErrorInnerWrapperSerializer()
	error = serializers.ListSerializer(child=serializers.CharField(), allow_null=True)

class ErrorAvailabilityTimeslotSingleUpdateFinalResponseWrapper(serializers.Serializer):
	errors = UpdateErrorOuterWrapperSerializer()

# TODO: fix the serializers
class HttpErrorAvailabilityTimeslotSingleUpdateResponse(HttpErrorResponseSerializer):
	data = ErrorAvailabilityTimeslotSingleUpdateFinalResponseWrapper()

class HttpAvailabilityTimeslotUpdateSuccessResponse(HttpSuccessResponeSerializer):
	data = AvailabilityTimeslotSingleUpdateSerializer()


class AvailabilityTimeSlotDestroySerializer(serializers.Serializer):

	force_drop = serializers.BooleanField(default=False)

	def validate(self, value):

		
			
		# 1. checking that no appointment linked to this timeslot fall out of the new interval, if froce drop is not true
		if not value.get('force_drop', False) and self.instance.linked_appointments.exists():
			raise ValidationError(message=_('The following appointments will be dropped: '), data={
				'dropped_appointments': AppointmentReadSerializer(instance=self.instance.linked_appointments, many=True).data
			})
		
		return value
	
	def to_representation(self, instance):
		return {
			'force_drop': self.validated_data.get('force_drop', False)
		}


# ---------- Appointments ----------
	



class AppointmentReadSerializer(serializers.ModelSerializer):
	"""Serializer for listing appointments"""
	
	timeslot = AvailabilityTimeslotReadSerializer()


	class Meta:
		model = Appointment
		fields = ['id', 'timeslot', 'patient', 'status', 'start_at', 'end_at']

class RawAppointmentReadSerializer(serializers.ModelSerializer):
	"""Serializer for listing appointments"""
	
	

	class Meta:
		model = Appointment
		fields = ['id', 'status', 'start_at', 'end_at']

class HttpAppointmentRetrieveSerializer(HttpSuccessResponeSerializer):
	"""Serializer used for swagger HTTP schema"""
	data = (AppointmentReadSerializer())

class PaginatedAppointmentReadSerializer(serializers.Serializer):
	"""Serializer for paginated appointment list"""
	results = AppointmentReadSerializer(many=True)

class HttpAppointmentListSerializer(HttpSuccessResponeSerializer):
	"""Serializer used for swagger HTTP schema"""
	data = PaginatedAppointmentReadSerializer()



class AppointmentCreateSerializer(serializers.ModelSerializer):
	"""Serializer for creating appointments"""

	def validate_start_at(self, value):
		if value < timezone.now():
			raise VE(_("APPOINTMENT START TIME CANNOT BE IN THE PAST"))
		return value
	
	def validate(self, attrs):
		"""
			validating that the proposed time is correct
		"""

		# 1. validate that the timeslot is within the availability timeslot
		timeslot = attrs['timeslot']
		start_at = attrs['start_at']
		end_at = attrs['end_at']

		if end_at < start_at:
			raise ValidationError( _('APPOINTMENT START TIME MUST BE BEFORE END TIME'))

		if start_at < timeslot.start_at or end_at > timeslot.end_at:
			raise ValidationError( _('APPOINTMENT TIME MUST BE WITHIN THE AVAILABILITY TIMESLOT'))
		
		# 2. validate that the owner of the timeslot is the user himself if the request was made by a therapist
		if hasattr(self.context['request'].user, 'therapist_profile') and timeslot.therapist != self.context['request'].user.therapist_profile:
			raise ValidationError( _('YOU CANNOT USE ANOTHER THERAPIST\'S TIMESLOT'))

		# 3. validate that the appointment does not conflict with other confirmed appointments if the therapist is the one creating the appointment
		if timeslot.linked_appointments.filter(
			Q(status=CONFIRMED) & Q(start_at__lte=end_at, end_at__gte=start_at) &
			Q(timeslot__therapist= timeslot.therapist)).exists():
		
			raise ValidationError( _('APPOINTMENT TIME CONFLICTS WITH ANOTHER CONFIRMED APPOINTMENT FOR SAME THERAPIST'))



		# 4. validate that start time is before end time
		if start_at >= end_at:
			raise ValidationError( _('APPOINTMENT START TIME MUST BE BEFORE END TIME'))

		return attrs
	


	def create(self, validated_data):

		# NOTE: not ideal in case of more roles, polymporhism is a better long-term solution
		if hasattr(self.context['request'].user, 'therapist_profile') :
			validated_data['status'] = 'PENDING_PATIENT'
			self.context['request'].user.therapist_profile ## forcing therapist to only create appointments for himself

		elif hasattr(self.context['request'].user, 'patient_profile'):
			validated_data['status'] = 'PENDING_THERAPIST'
			validated_data['patient'] = self.context['request'].user.patient_profile ## forcing patient to only create appointments for himself    

		# create a therapist assignment for the appointment

		result =  super().create(validated_data)

		TherapistAssignment.objects.create(
			therapist_timeslot=validated_data['timeslot'],
			status= ACTIVE,
			appointment= result
		)

		return result

	class Meta:
		model = Appointment
		fields = ['timeslot', 'patient', 'start_at', 'end_at', 'id']

class AppointmentCreateErrorInnerWrapperSerializer(serializers.Serializer):
	"""Serializer used for Signup credential validation on data level"""
	timeslot = serializers.ListSerializer(child=serializers.CharField(allow_blank=True, max_length=150), allow_null=True)
	patient = serializers.ListSerializer(child=serializers.CharField(allow_blank=True, max_length=128), allow_null=True)
	start_at = serializers.ListSerializer(child=serializers.CharField(allow_blank=True, max_length=128), allow_null=True)
	end_at = serializers.ListSerializer(child=serializers.CharField(allow_blank=True, max_length=128), allow_null=True)
	error = serializers.ListSerializer(child=serializers.CharField(allow_blank=True, max_length=128), allow_null=True)

class AppointmentCreateErrorOuterWrapperSerializer(serializers.Serializer):
	errors = AppointmentCreateErrorInnerWrapperSerializer()

class HttpErrAppointmentCreateSerializer(HttpErrorResponseSerializer):
	"""Serializer used for swagger HTTP schema"""
	data = AppointmentCreateErrorOuterWrapperSerializer()


class HttpAppointmentCreateSerializer(HttpSuccessResponeSerializer):
	"""Serializer used for swagger HTTP schema"""
	data = AppointmentReadSerializer()

# TODO: create custom validation to exclude the appointment itself from validation
class AppointmentUpdateSerializer(AppointmentCreateSerializer):
	"""Serializer for updating appointments"""

	def validate(self, attrs):

		timeslot = attrs.get('timeslot', None) or self.instance.timeslot
		start_at = attrs.get('start_at', None) or self.instance.start_at
		end_at = attrs.get('end_at', None) or self.instance.end_at
		therapist = self.instance.timeslot.therapist
		if start_at < timeslot.start_at or end_at > timeslot.end_at:
			raise ValidationError(_('APPOINTMENT TIME MUST BE WITHIN THE AVAILABILITY TIMESLOT'))

		if start_at < timezone.now():
			raise ValidationError(_('APPOINTMENT CANNOT START IN THE PAST'))

		# 2. validate that the appointment does not conflict with other confirmed appointments
		if timeslot.linked_appointments.filter(
			~Q(pk=self.instance.pk) &
			Q(status=CONFIRMED) & Q(start_at__lte=end_at, end_at__gte=start_at) &
			Q(timeslot__therapist=therapist
							)).exists():
			raise ValidationError(_('APPOINTMENT TIME CONFLICTS WITH ANOTHER CONFIRMED APPOINTMENT'))

		# 3. validate that start time is before end time
		if start_at >= end_at:
			raise ValidationError(_('APPOINTMENT START TIME MUST BE BEFORE END TIME'))

		return attrs

	def update(self, instance, validated_data):
		
		old_timeslot = instance.timeslot.pk
		new_timeslot = validated_data.get('timeslot', instance.timeslot).pk
		result =  super().update(instance, validated_data)

		if old_timeslot != new_timeslot:
			TherapistAssignment.objects.create(
				therapist_timeslot=validated_data['timeslot'],
				status= ACTIVE,
				appointment= instance
			)

		return result
	
	class Meta:
		model = AppointmentCreateSerializer.Meta.model
		fields = ['timeslot', 'start_at', 'end_at', 'id']


class HttpSuccessAppointmentUpdateSerializer(HttpSuccessResponeSerializer):
	"""Serializer used for swagger HTTP schema"""
	data = AppointmentUpdateSerializer()


class AppointmentUpdateErrorInnerWrapperSerializer(serializers.Serializer):
	"""Serializer used for Signup credential validation on data level"""
	timeslot = serializers.ListSerializer(child=serializers.CharField(allow_blank=True, max_length=150), allow_null=True)
	start_at = serializers.ListSerializer(child=serializers.CharField(allow_blank=True, max_length=128), allow_null=True)
	end_at = serializers.ListSerializer(child=serializers.CharField(allow_blank=True, max_length=128), allow_null=True)
	error = serializers.ListSerializer(child=serializers.CharField(allow_blank=True, max_length=128), allow_null=True)

class AppointmentUpdateErrorOuterWrapperSerializer(serializers.Serializer):
	errors = AppointmentUpdateErrorInnerWrapperSerializer()

class HttpErrAppointmentUpdateSerializer(HttpErrorResponseSerializer):
	"""Serializer used for swagger HTTP schema"""
	data = AppointmentUpdateErrorOuterWrapperSerializer()


class DestroyAvailabilityTimeslotErrorInnerWrapperSerializer(serializers.Serializer):
	dropped_appointments = AppointmentReadSerializer(many=True, allow_null=True)
class HttpErrorAvailabilityTimeslotDestroyErrorResponse(HttpErrorSerializer):
	data = DestroyAvailabilityTimeslotErrorInnerWrapperSerializer()