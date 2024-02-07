from rest_framework import serializers
from appointments.models import Appointment, AvailabilityTimeSlot
from appointments.serializers.timeslots import AvailabilityTimeslotReadSerializer
from core.http import ValidationError

from core.serializers import  HttpSuccessResponeSerializer, paginate_serializer
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

class HttpAppointmentListSerializer(HttpSuccessResponeSerializer):
    """Serializer used for swagger HTTP schema"""
    data = paginate_serializer(AppointmentReadSerializer())



class AppointmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating appointments"""
    
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

        return attrs


    class Meta:
        model = Appointment
        fields = ['timeslot', 'patient', 'status', 'start_at', 'end_at']

class AppointmentUpdateSerializer(serializers.Serializer):
    """Serializer for updating appointments"""
    pass

class AppointmentAssignmentDropSerializer(serializers.Serializer):
    """Serializer for dropping an appointment assignment"""
    pass

class AppointmentFeedbackReadSerializer(serializers.ModelSerializer):
    """Serializer for listing appointment feedbacks"""
    pass

class HttpAppointmentFeedbackListSerializer(HttpSuccessResponeSerializer):
    """Serializer for listing appointment feedbacks"""
    data = AppointmentFeedbackReadSerializer(many=True)

class HttpAppointmentFeedbackRetrieveSerializer(HttpSuccessResponeSerializer):
    """Serializer for listing appointment feedbacks"""
    data = AppointmentFeedbackReadSerializer()


class AppointmentFeedbackCreateSerializer(serializers.Serializer):
    """Serializer for creating appointment feedbacks"""
    pass
