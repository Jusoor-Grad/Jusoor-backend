from typing import Dict, List
from pytz import timezone
from rest_framework import serializers
from appointments.models import AvailabilityTimeSlot
from authentication.serializers import TherapistReadSerializer
from core.http import ValidationError
from core.models import Therapist
from core.serializers import HttpErrorResponseSerializer, HttpSuccessResponeSerializer, HttpPaginatedSerializer
from django.utils.translation import gettext as _
from django.db.models import Q

class AvailabilityTimeslotReadSerializer(serializers.ModelSerializer):
    """Serializer for listing availability timeslots"""
    therapist = serializers.SerializerMethodField()

    def get_therapist(self, instance):

        return TherapistReadSerializer(instance=instance.therapist.user).data
    
    class Meta:
        model = AvailabilityTimeSlot
        fields = ['id', 'therapist', 'start_at', 'end_at', 'created_at']

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


class WeekRepresentationSerializer(serializers.Serializer):

    sunday = TimeIntervalSerializer(many=True, allow_empty=False, allow_null=True, required=False)
    monday = TimeIntervalSerializer(many=True, allow_empty=False, allow_null=True, required=False)
    tuesday = TimeIntervalSerializer(many=True, allow_empty=False, allow_null=True, required=False)
    wednesday = TimeIntervalSerializer(many=True, allow_empty=False, allow_null=True, required=False)
    thursday = TimeIntervalSerializer(many=True, allow_empty=False, allow_null=True, required=False)

    def validate(self, attrs):

        if not any([attrs.get('sunday'), attrs.get('monday'), attrs.get('tuesday'), attrs.get('wednesday'), attrs.get('thursday')]):
            raise ValidationError('At least one day must be selected')

        return attrs


class AvailabilityTimeslotCreateSerializer(serializers.Serializer):
    """
        Serializer to create availabiltiy timslots for a single week only
    """
    
    intervals = DatetimeIntervalSerializer(many=True, allow_empty=False, allow_null=False, required=True)


    def validate_intervals(self, intervals):
        """
        Collecting all possible interval conflict errors and raise at once
        to avoid user frustration
        """

        sorted_intervals = sorted(intervals, key=lambda interval: interval['start_at'], reverse=False)

        uploaded_timeslot_conflict_pairs= []

        for i in range(len(sorted_intervals) - 1):
            current_interval = sorted_intervals[i]
            next_interval = sorted_intervals[i + 1]

            if current_interval['end_at'] > next_interval['start_at']:
                uploaded_timeslot_conflict_pairs.append([current_interval, next_interval])

        # getting all possible conflicting timeslots to avoid fetching each record in a loop
        possible_conflicting_timeslots = AvailabilityTimeSlot.objects.filter(
            Q(therapist= Therapist.objects.get(user=self.context['request'].user)) & 

            (Q(start_at__lte=sorted_intervals[0]['start_at'], end_at__gte=sorted_intervals[0]['start_at']) |
            Q(start_at__lte=sorted_intervals[-1]['end_at'], end_at__gte=sorted_intervals[-1]['end_at'])
            )
            
        )

        existing_timeslot_conflicts =[ ]

        # checking for between uploaded intervals and existing intervals
        for interval in sorted_intervals:
            if possible_conflicting_timeslots.filter(
                Q(start_at__lte=interval['start_at'], end_at__gte=interval['start_at']) |
                Q(start_at__lte=interval['end_at'], end_at__gte=interval['end_at'])
            ).exists():
                existing_timeslot_conflicts.append(interval)

        if len(existing_timeslot_conflicts) > 0 or len(uploaded_timeslot_conflict_pairs) > 0:
            raise ValidationError(message=_('The following intervals conflict with existing timeslots: '), data={
                'existing_timeslot_conflicts': existing_timeslot_conflicts,
                'uploaded_timeslot_conflict_pairs': uploaded_timeslot_conflict_pairs
            })

        return intervals

    def create(self, validated_data):
        
        for interval in validated_data['intervals']:
            AvailabilityTimeSlot.objects.create(
                therapist= Therapist.objects.get(user=self.context['request'].user),
                start_at=interval['start_at'],
                end_at=interval['end_at']
            )

        return validated_data


class AvailabilityTimeslotBatchCreateUploadSerializer(FutureDatetimeIntervalSerializer):
    """
        Serializer used solely to validate the uploaded schedule
        validation of conflcit will be deon by the normal serializer
        afterwards
    """

    weekly_schedule = WeekRepresentationSerializer(allow_null=False)
    

# --------------- Swagger formatting serializers ------------

class HttpAvailabilityTimeslotCreateResponseSerializer(serializers.Serializer):

    data = AvailabilityTimeslotCreateSerializer()
    
class CreateErrorContentSerializer(serializers.Serializer):
    existing_timeslot_conflicts = DatetimeIntervalSerializer(many=True)
    uploaded_timeslot_conflict_pairs = serializers.ListSerializer(child=DatetimeIntervalSerializer(many=True))
class CreateErrorInnerWrapperSerializer(serializers.Serializer):
    error = serializers.CharField()
    data = CreateErrorContentSerializer()

class CreateErrorOuterWrapperSerializer(serializers.Serializer):
    intervals = CreateErrorInnerWrapperSerializer()

class HttpCreateTimeslotRawErrorSerializer(serializers.Serializer):
    errors = CreateErrorOuterWrapperSerializer()

class HttpErrorAvailabilityTimeslotResponse(HttpErrorResponseSerializer):
    data = HttpCreateTimeslotRawErrorSerializer()


    



class AvailabilityTimeslotBatchUpdateSerializer(serializers.Serializer):
    """Serializer for updating availability timeslots"""
    start_at = serializers.DateTimeField(required=True)
    timeslot_group = serializers.IntegerField(required=True)
    days = WeekRepresentationSerializer()
    force_drop = serializers.BooleanField(default=False)


class AvailabilityTimeslotSingleUpdateSerializer(serializers.ModelSerializer):
    """
        Serializer for updating a single availability timeslot
    """

    class Meta:
        model = AvailabilityTimeSlot
        fields = ['start_at', 'end_at']

