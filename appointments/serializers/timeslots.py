from rest_framework import serializers
from appointments.models import AvailabilityTimeSlot
from authentication.serializers import TherapistReadSerializer
from core.serializers import HttpResponeSerializer


class AvailabilityTimeslotReadSerializer(serializers.ModelSerializer):
    """Serializer for listing availability timeslots"""
    therapist = serializers.SerializerMethodField()

    def get_therapist(self, instance):

        return TherapistReadSerializer(instance=instance.therapist.user).data
    
    class Meta:
        model = AvailabilityTimeSlot
        fields = ['id', 'therapist', 'start_at', 'end_at', 'created_at']

class HttpAvailabilityTimeslotListSerializer(HttpResponeSerializer):
    """Serializer for listing availability timeslots"""
    data = AvailabilityTimeslotReadSerializer(many=True)

class HttpAvailabilityTimeslotRetrieveSerializer(HttpResponeSerializer):
    """Serializer for listing availability timeslots"""
    data = AvailabilityTimeslotReadSerializer()


class AvailabilityTimeslotCreateSerializer(serializers.Serializer):
    """Serializer for creating availability timeslots"""
    pass

class AvailabilityTimeslotUpdateSerializer(serializers.Serializer):
    """Serializer for updating availability timeslots"""
    pass
