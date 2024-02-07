from rest_framework import serializers
from appointments.models import AvailabilityTimeSlot
from authentication.serializers import TherapistReadSerializer
from core.serializers import HttpSuccessResponeSerializer, paginate_serializer


class AvailabilityTimeslotReadSerializer(serializers.ModelSerializer):
    """Serializer for listing availability timeslots"""
    therapist = serializers.SerializerMethodField()

    def get_therapist(self, instance):

        return TherapistReadSerializer(instance=instance.therapist.user).data
    
    class Meta:
        model = AvailabilityTimeSlot
        fields = ['id', 'therapist', 'start_at', 'end_at', 'created_at']

class HttpAvailabilityTimeslotListSerializer(HttpSuccessResponeSerializer):
    """Serializer for listing availability timeslots"""
    data = paginate_serializer(AvailabilityTimeslotReadSerializer(many=True))

class HttpAvailabilityTimeslotRetrieveSerializer(HttpSuccessResponeSerializer):
    """Serializer for listing availability timeslots"""
    data = AvailabilityTimeslotReadSerializer()


class IntervalSerializer(serializers.Serializer):
    """Serializer for listing availability timeslots"""
    start_at = serializers.DateTimeField()
    end_at = serializers.DateTimeField()


class WeekRepresentationSerializer(serializers.Serializer):

    sunday = IntervalSerializer(many=True, allow_empty=False, allow_null=True, required=False)
    monday = IntervalSerializer(many=True, allow_empty=False, allow_null=True, required=False)
    tuesday = IntervalSerializer(many=True, allow_empty=False, allow_null=True, required=False)
    wednesday = IntervalSerializer(many=True, allow_empty=False, allow_null=True, required=False)
    thursday = IntervalSerializer(many=True, allow_empty=False, allow_null=True, required=False)

    def validate(self, attrs):

        if not any([attrs.get('sunday'), attrs.get('monday'), attrs.get('tuesday'), attrs.get('wednesday'), attrs.get('thursday')]):
            raise serializers.ValidationError('At least one day must be selected')

        return attrs

    def create(self, validated_data):
        return super().create(validated_data)



class AvailabilityTimeslotCreateSerializer(IntervalSerializer):
    """Serializer for creating availability timeslots"""
    start_at = serializers.DateTimeField()
    end_at = serializers.DateTimeField()
    days = WeekRepresentationSerializer(many=True)

class AvailabilityTimeslotUpdateSerializer(serializers.Serializer):
    """Serializer for updating availability timeslots"""
    pass
