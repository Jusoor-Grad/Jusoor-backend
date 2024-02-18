
from rest_framework import serializers
from appointments.constants.enums import ACCEPTED, PENDING, PENDING_THERAPIST, REJECTED, WEEK_DAYS
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

		if PatientReferralRequest.objects.filter(referrer=attrs['referrer'], referee=attrs['referee'], status=PENDING).exists():
			raise ValidationError(_('A referral request already exists for this referee'))

		if not hasattr(attrs['referee'], 'patient_profile'):
			raise ValidationError(_('The referee is not a patient'))

		return attrs 
	class Meta:
		model = PatientReferralRequest
		fields = [ 'referee', 'reason']

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
		
		if not PatientReferralRequest.objects.filter(pk=self.instance.pk, status=PENDING).exists():
			raise ValidationError(_('Referral request is not pending'))

		return attrs

	class Meta:
		model = PatientReferralRequest
		fields = ['referee', 'reason']


class HttpReferralRequestUpdateResponseSerializer(HttpSuccessResponeSerializer):
	"""Serializer for updating referral requests"""
	data = ReferralRequestUpdateSerializer()


class ReferralRequestReplySerializer(serializers.ModelSerializer):

	status = serializers.ChoiceField(choices=[ACCEPTED, REJECTED])

	class Meta:
		model = PatientReferralRequest
		fields = ['status']

	def validate(self, attrs):

		if not PatientReferralRequest.objects.filter(pk=self.instance.pk, status=PENDING).exists():
			raise ValidationError(_('Referral request is not pending'))


		return attrs

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
	status = serializers.ListSerializer(child=serializers.CharField(allow_blank=True, max_length=150))
	error = serializers.ListSerializer(child=serializers.CharField(allow_blank=True, max_length=128))

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

class AvailabilityTimeslotReadSerializer(serializers.ModelSerializer):
	"""Serializer for listing availability timeslots"""
	therapist = serializers.SerializerMethodField()

	linked_appointments = serializers.SerializerMethodField()

	def get_linked_appointments(self, instance):
		return RawAppointmentReadSerializer(instance=instance.linked_appointments, many=True).data

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


	def validate_intervals(self, intervals):
		"""
		Collecting all possible interval conflict errors and raise at once
		to avoid user frustration
		"""

		sorted_intervals = sorted(intervals, key=lambda interval: interval, reverse=False)


		# getting all possible conflicting timeslots to avoid fetching each record in a loop
		possible_conflicting_timeslots = AvailabilityTimeSlot.objects.filter(
			Q(therapist= Therapist.objects.get(user=self.context['request'].user)) & 

			(Q(start_at__lte=sorted_intervals[0]['start_at'], end_at__gte=sorted_intervals[0]['start_at']) |
			Q(start_at__lte=sorted_intervals[-1]['end_at'], end_at__gte=sorted_intervals[-1]['end_at'])
			)
			
		)

		existing_timeslot_conflicts =[]

		# checking for between uploaded intervals and existing intervals
		for interval in sorted_intervals:
			conflicting_intervals = possible_conflicting_timeslots.filter(
				Q(start_at__lte=interval['start_at'], end_at__gte=interval['start_at']) |
				Q(start_at__lte=interval['end_at'], end_at__gte=interval['end_at'])
			)
			# if there exists existing intervals that are conflict supply the uploaded interval, and all existing conflicting intervals
			if conflicting_intervals.exists():
				existing_timeslot_conflicts.append({
					'interval': interval,
					'conflicting_timeslots': AvailabilityTimeslotReadSerializer(instnace=conflicting_intervals, many=True).data
				
				})

		if len(existing_timeslot_conflicts) > 0:
			raise ValidationError(message=_('The following intervals conflict with existing timeslots: '), data={
				'existing_timeslot_conflicts': existing_timeslot_conflicts,
			})

		return intervals

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
			# filter to get all timeslots with any region possibly contained within the new declared timeslots
			((Q(start_at__lte=attrs['start_at'], end_at__lte=attrs['end_at'], end_at__gte=attrs['start_at']) |
			Q(start_at__lte=attrs['end_at'], start_at__gte=attrs['start_at'], end_at__gte=attrs['end_at'])) | 
			# checking if timeslot is fully contained within a single timeslot
			Q(start_at__gte=attrs['start_at'], end_at__lte=attrs['end_at']) |
			# checking if a single timeslots spans the full specified timeslot
			Q(start_at__lte=attrs['start_at'], end_at__gte=attrs['end_at']))
			)
		print('POSSIIBLE CONFLICTS', possible_conflicting_timeslots)
		print('THERAPIST', Therapist.objects.get(user=self.context['request'].user).pk)
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
					(Q(start_at__lte=interval['start_at'], end_at__gte=interval['start_at']) |
					Q(start_at__lte=interval['end_at'], end_at__gte=interval['end_at']))
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
	existing_timeslot_conflicts = DatetimeIntervalSerializer(many=True)
	uploaded_timeslot_conflict_pairs = serializers.ListSerializer(child= SingleTimeslotErrorSerializer())

class BatchCreateErrorContentSerializer(serializers.Serializer):
	uploaded_timeslot_conflict_pairs = serializers.ListSerializer(child= SingleTimeslotErrorSerializer())

class CreateErrorInnerWrapperSerializer(serializers.Serializer):
  
	data = SingleCreateErrorContentSerializer()

class BatchCreateErrorInnerWrapperSerializer(serializers.Serializer):
	
	sunday = SingleCreateErrorContentSerializer()
	monday = SingleCreateErrorContentSerializer()
	tuesday = SingleCreateErrorContentSerializer()
	wednesday = SingleCreateErrorContentSerializer()
	thursday = SingleCreateErrorContentSerializer()

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

		# for partial updating, we need to get the missing start and end times from the instance
		start_at = value['start_at'] or self.instance.start_at.time()
		end_at = value['end_at'] or self.instance.end_at.time()

		# 1. checking for conflict with other timeslots by the same therapist
		conflicting_timeslots = AvailabilityTimeSlot.objects.annotate(
			weekday= ExtractWeekDay('start_at'),
		).filter(
			Q(therapist= Therapist.objects.get(user=self.context['request'].user)) &
			Q(weekday=(self.instance.start_at.weekday() + 2) % 7) &
			~Q(pk=self.instance.pk) & 
			(Q(start_at__time__lte=start_at, end_at__time__gte=start_at) |
			Q(start_at__time__lte=end_at, end_at__time__gte=end_at))
			)
		
		if conflicting_timeslots.exists():
			raise ValidationError(message=_('The following timeslots conflict with new updated timeslots: '), data={
				'conflicting_timeslots': AvailabilityTimeslotReadSerializer(instance=conflicting_timeslots, many=True).data
			})
		
		# 2. checking that no appointment linked to this timeslot fall out of the new interval, if froce drop is not true
		if value.get('force_drop', False):
			appointments = self.instance.linked_appointments.annotate(
				weekday= ExtractWeekDay('start_at'),
			).filter(
				Q(weekday=(self.instance.start_at.weekday() + 2) % 7) &
				Q(start_at__time__lt=value['start_at']) | Q(end_at__time__gt=value['end_at'])
			)

			# TODO: include in error object
			if appointments.exists():
				raise ValidationError(message=_('The following appointments fall out of the new interval: '), data={
					'dropped_appointments': AppointmentReadSerializer(instance=appointments, many=True).data
				})
		
		return value



	def update(self, instance, validated_data):
		
		# create a new availability timeslot group for the updated group of updated intervals
		group = AvailabilityTimeSlotGroup.objects.create()
		# drop any appointments outside the boundaries of new intervals
		if validated_data.get('force_drop', True):
			Appointment.objects.annotate(weekday = ExtractWeekDay('start_at')).filter(
				Q(timeslot__group=instance.group) &
				Q(weekday=(instance.start_at.weekday() + 2) % 7) &
				# filtering appointments that were originally inside timeslot and now outside
				(Q(start_at__time__lt=validated_data['start_at']) | Q(end_at__time__gt=validated_data['end_at']))
			).update(timeslot=None)

		affected_slots = AvailabilityTimeSlot.objects\
		.annotate(weekday= ExtractWeekDay('start_at'), 
		start_hour=ExtractHour('start_at'),
		start_minute=ExtractMinute('start_at'),
		end_hour=ExtractHour('end_at'),
		end_minute=ExtractMinute('end_at')).filter(
			# get all parallel timeslots with same group and time range
			Q(group=instance.group)&
			Q(weekday = (instance.start_at.weekday() + 2) % 7) & 
			Q(start_hour=instance.start_at.hour) &
			Q(start_minute=instance.start_at.minute) &
			Q(end_hour=instance.end_at.hour) &
			Q(end_minute=instance.end_at.minute) &
			Q(start_at__gte = instance.start_at) ## only update future timeslots only
			)
		
		
		for timeslot in affected_slots:
			print(timeslot.start_at.strftime("%A"), instance.start_at.strftime("%A"))
			timeslot.group=group
			timeslot.start_at = datetime.combine(timeslot.start_at, validated_data['start_at']) 
			timeslot.end_at = datetime.combine(timeslot.end_at, validated_data['end_at'])

		AvailabilityTimeSlot.objects.bulk_update(affected_slots, ['group', 'start_at', 'end_at'])

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
			(Q(start_at__lte=start_at, end_at__gte=start_at) |
			Q(start_at__lte=end_at, end_at__gte=end_at))
			)

		if conflicting_timeslots.exists():
			raise ValidationError(message=_('The following intervals conflict with existing timeslots: '), data={
				'interval': attrs,
				'conflicting_timeslots': AvailabilityTimeslotReadSerializer(instance=conflicting_timeslots, many=True).data
			})

		# 2. checking that no appointment linked to this timeslot fall out of the new interval, if froce drop is not true
		if attrs.get('force_drop', False):
			appointments = self.instance.linked_appointments.filter(
				Q(start_at__lt=start_at) | Q(end_at__gt=end_at)
			)
			# TODO: include in error object
			if appointments.exists():
				raise ValidationError(message=_('The following appointments fall out of the new interval: '), data={
					'dropped_appointments': AppointmentReadSerializer(instance=appointments, many=True).data
				})
			
		return attrs
		

	def update(self, instance, validated_data):

		# drop all appointments falling out of range when using force drop
		if validated_data.get('force_drop', True):
			instance.linked_appointments.filter(
				Q(start_at__lt=validated_data['start_at']) | Q(end_at__gt=validated_data['end_at'])
			).update(timeslot=None)

		start_at = self.instance.start_at.combine(self.instance.start_at.date(), validated_data['start_at'])
		end_at = self.instance.end_at.combine(self.instance.end_at.date(), validated_data['end_at'])

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
	error = serializers.ListSerializer(child=serializers.CharField())

class ErrorAvailabilityTimeslotSingleUpdateFinalResponseWrapper(serializers.Serializer):
	errors = UpdateErrorOuterWrapperSerializer()

# TODO: fix the serializers
class HttpErrorAvailabilityTimeslotSingleUpdateResponse(HttpErrorResponseSerializer):
	data = ErrorAvailabilityTimeslotSingleUpdateFinalResponseWrapper()

class HttpAvailabilityTimeslotUpdateSuccessResponse(HttpSuccessResponeSerializer):
	data = AvailabilityTimeslotSingleUpdateSerializer()


class AvailabilityTimeSlotDestroySerializer(serializers.ModelSerializer):

	force_drop = serializers.BooleanField(default=False)

	def validate(self, attrs):
		
		# 1. checking that no appointment linked to this timeslot fall out of the new interval, if froce drop is not true
		if attrs.get('force_drop', False) and self.instance.linked_appointments.exists():
			raise ValidationError(message=_('The following appointments will be dropped: '), data={
				'dropped_appointments': AppointmentReadSerializer(instance=self.instance.linked_appointments, many=True).data
			})
		
		return attrs


	class Meta:
		model = AvailabilityTimeSlot
		fields = ['id', 'force_drop']

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
		fields = ['id', 'patient', 'status', 'start_at', 'end_at']

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

		# 2. validate that the appointment does not conflict with other confirmed appointment
		if timeslot.linked_appointments.filter(
			Q(status='CONFIRMED') & (Q(start_at__lte=start_at, end_at__gte=start_at) | Q(start_at__lte=end_at, end_at__gte=end_at))).exists():
			raise ValidationError( _('APPOINTMENT TIME CONFLICTS WITH ANOTHER CONFIRMED APPOINTMENT'))

		# 3. validate that the owner of the timeslot is the user himself if the request was made by a therapist
		if self.context['request'].user.therapist_profile is not None and timeslot.therapist != self.context['request'].user.therapist_profile:
			raise ValidationError( _('YOU CANNOT USE ANOTHER THERAPIST\'S TIMESLOT'))


		# 4. validate that start time is before end time
		if start_at >= end_at:
			raise ValidationError( _('APPOINTMENT START TIME MUST BE BEFORE END TIME'))

		return attrs
	


	def create(self, validated_data):

		# NOTE: not ideal in case of more roles, polymporhism is a better long-term solution
		if self.context['request'].user.therapist_profile is not None:
			validated_data['status'] = 'PENDING_PATIENT'
		elif self.context['request'].user.patient_profile is not None:
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
	timeslot = serializers.ListSerializer(child=serializers.CharField(allow_blank=True, max_length=150))
	patient = serializers.ListSerializer(child=serializers.CharField(allow_blank=True, max_length=128))
	start_at = serializers.ListSerializer(child=serializers.CharField(allow_blank=True, max_length=128))
	end_at = serializers.ListSerializer(child=serializers.CharField(allow_blank=True, max_length=128))
	error = serializers.ListSerializer(child=serializers.CharField(allow_blank=True, max_length=128))

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

		timeslot = attrs['timeslot'] or self.instance.timeslot
		start_at = attrs['start_at'] or self.instance.start_at
		end_at = attrs['end_at'] or self.instance.end_at
		if start_at < timeslot.start_at or end_at > timeslot.end_at:
			raise ValidationError(_('APPOINTMENT TIME MUST BE WITHIN THE AVAILABILITY TIMESLOT'))

		if start_at < timezone.now():
			raise ValidationError(_('APPOINTMENT CANNOT START IN THE PAST'))

		# 2. validate that the appointment does not conflict with other confirmed appointment
		if timeslot.linked_appointments.filter(
			~Q(pk=self.instance.pk) &
			Q(status='CONFIRMED') & (Q(start_at__lte=start_at, end_at__gte=start_at) | Q(start_at__lte=end_at, end_at__gte=end_at))).exists():
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
		fields = ['timeslot', 'status', 'start_at', 'end_at', 'id']


class HttpSuccessAppointmentUpdateSerializer(HttpSuccessResponeSerializer):
	"""Serializer used for swagger HTTP schema"""
	data = AppointmentUpdateSerializer()


class AppointmentUpdateErrorInnerWrapperSerializer(serializers.Serializer):
	"""Serializer used for Signup credential validation on data level"""
	timeslot = serializers.ListSerializer(child=serializers.CharField(allow_blank=True, max_length=150))
	start_at = serializers.ListSerializer(child=serializers.CharField(allow_blank=True, max_length=128))
	end_at = serializers.ListSerializer(child=serializers.CharField(allow_blank=True, max_length=128))
	error = serializers.ListSerializer(child=serializers.CharField(allow_blank=True, max_length=128))

class AppointmentUpdateErrorOuterWrapperSerializer(serializers.Serializer):
	errors = AppointmentUpdateErrorInnerWrapperSerializer()

class HttpErrAppointmentUpdateSerializer(HttpErrorResponseSerializer):
	"""Serializer used for swagger HTTP schema"""
	data = AppointmentUpdateErrorOuterWrapperSerializer()


class DestroyAvailabilityTimeslotErrorInnerWrapperSerializer(serializers.Serializer):
	dropped_appointments = AppointmentReadSerializer(many=True, allow_null=True)
class HttpErrorAvailabilityTimeslotDestroyErrorResponse(HttpErrorSerializer):
	data = DestroyAvailabilityTimeslotErrorInnerWrapperSerializer()