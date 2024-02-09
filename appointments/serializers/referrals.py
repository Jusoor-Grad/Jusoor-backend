from regex import P
from rest_framework import serializers
from appointments.constants.enums import ACCEPTED, PENDING, PENDING_THERAPIST, REJECTED
from appointments.models import Appointment, PatientReferralRequest
from authentication.serializers import UserReadSerializer
from core.http import ValidationError
from core.serializers import HttpSuccessResponeSerializer
from django.utils.translation import gettext as _

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