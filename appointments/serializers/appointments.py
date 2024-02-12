from rest_framework import serializers
from appointments.constants.enums import ACTIVE
from appointments.models import Appointment, AvailabilityTimeSlot, TherapistAssignment
from appointments.serializers.timeslots import AvailabilityTimeslotReadSerializer
from core.http import ValidationError
from django.utils import timezone
from core.serializers import  HttpSuccessResponeSerializer
from django.db.models import Q
from django.utils.translation import gettext as _


# ---------- Appointments ----------

class AppointmentReadSerializer(serializers.ModelSerializer):
    """Serializer for listing appointments"""
    
    timeslot = AvailabilityTimeslotReadSerializer()


    class Meta:
        model = Appointment
        fields = ['id', 'timeslot', 'patient', 'status', 'start_at', 'end_at']

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
            raise ValidationError(_("APPOINTMENT START TIME CANNOT BE IN THE PAST"))
        return value
    
    def validate(self, attrs):
        """
            validating that the proposed time is correct
        """

        # 1. validate that the timeslot is within the availability timeslot
        timeslot = attrs['timeslot']
        start_at = attrs['start_at']
        end_at = attrs['end_at']

        if start_at < timeslot.start_at or end_at > timeslot.end_at:
            raise ValidationError({"timeslot": _('APPOINTMENT TIME MUST BE WITHIN THE AVAILABILITY TIMESLOT')})

        # 2. validate that the appointment does not conflict with other confirmed appointment
        if timeslot.linked_appointments.filter(
            Q(status='CONFIRMED') & (Q(start_at__lte=start_at, end_at__gte=start_at) | Q(start_at__lte=end_at, end_at__gte=end_at))).exists():
            raise ValidationError({"timeslot": _('APPOINTMENT TIME CONFLICTS WITH ANOTHER CONFIRMED APPOINTMENT')})

        # 3. validate that the owner of the timeslot is the user himself if the request was made by a therapist
        if self.context['request'].user.therapist_profile is not None and timeslot.therapist != self.context['request'].user.therapist_profile:
            raise ValidationError({"timeslot": _('YOU CANNOT USE ANOTHER THERAPIST\'S TIMESLOT')})


        # 4. validate that start time is before end time
        if start_at >= end_at:
            raise ValidationError({"start_at": _('APPOINTMENT START TIME MUST BE BEFORE END TIME')})

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
            raise ValidationError({_('APPOINTMENT TIME MUST BE WITHIN THE AVAILABILITY TIMESLOT')})

        if start_at < timezone.now():
            raise ValidationError(_('APPOINTMENT CANNOT START IN THE PAST'))

        # 2. validate that the appointment does not conflict with other confirmed appointment
        if timeslot.linked_appointments.filter(
            ~Q(pk=self.instance.pk) &
            Q(status='CONFIRMED') & (Q(start_at__lte=start_at, end_at__gte=start_at) | Q(start_at__lte=end_at, end_at__gte=end_at))).exists():
            raise ValidationError({_('APPOINTMENT TIME CONFLICTS WITH ANOTHER CONFIRMED APPOINTMENT')})

        # 3. validate that start time is before end time
        if start_at >= end_at:
            raise ValidationError({_('APPOINTMENT START TIME MUST BE BEFORE END TIME')})

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


class HttpAppointmentUpdateSerializer(HttpSuccessResponeSerializer):
    """Serializer used for swagger HTTP schema"""
    data = AppointmentUpdateSerializer()