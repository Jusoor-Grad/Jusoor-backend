from rest_framework import serializers
from appointments.models import Appointment
from appointments.serializers.timeslots import AvailabilityTimeslotReadSerializer

from core.serializers import HttpSuccessResponeSerializer



# ---------- Appointments ----------

class AppointmentReadSerializer(serializers.ModelSerializer):
    """Serializer for listing appointments"""
    
    timeslot = AvailabilityTimeslotReadSerializer()

    class Meta:
        model = Appointment
        fields = ['id', 'timeslot', 'patient', 'status', 'start_at', 'end_at']

class HttpAppointmentRetrieveSerializer(HttpSuccessResponeSerializer):
    """Serializer used for swagger HTTP schema"""
    data = AppointmentReadSerializer(many=True)

class HttpAppointmentRetrieveSerializer(HttpSuccessResponeSerializer):
    """Serializer used for swagger HTTP schema"""
    data = AppointmentReadSerializer()


class AppointmentCreateSerializer(serializers.Serializer):
    """Serializer for creating appointments"""
    pass

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
