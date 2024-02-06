from rest_framework import serializers
from appointments.models import Appointment
from appointments.serializers.timeslots import AvailabilityTimeslotReadSerializer

from core.serializers import HttpResponeSerializer



# ---------- Appointments ----------

class AppointmentReadSerializer(serializers.ModelSerializer):
    """Serializer for listing appointments"""
    
    timeslot = AvailabilityTimeslotReadSerializer()

    class Meta:
        model = Appointment
        fields = ['id', 'timeslot', 'patient', 'status', 'start_at', 'end_at']

class HttpAppointmentRetrieveSerializer(HttpResponeSerializer):
    """Serializer used for swagger HTTP schema"""
    data = AppointmentReadSerializer(many=True)

class HttpAppointmentRetrieveSerializer(HttpResponeSerializer):
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

class HttpAppointmentFeedbackListSerializer(HttpResponeSerializer):
    """Serializer for listing appointment feedbacks"""
    data = AppointmentFeedbackReadSerializer(many=True)

class HttpAppointmentFeedbackRetrieveSerializer(HttpResponeSerializer):
    """Serializer for listing appointment feedbacks"""
    data = AppointmentFeedbackReadSerializer()


class AppointmentFeedbackCreateSerializer(serializers.Serializer):
    """Serializer for creating appointment feedbacks"""
    pass
