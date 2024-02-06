from rest_framework import serializers
from core.serializers import HttpResponeSerializer


class ReferralRequestReadSerializer(serializers.ModelSerializer):
    """Serializer for listing referral requests"""
    pass

class HttpReferralRequestListSerializer(HttpResponeSerializer):
    """Serializer for listing referral requests"""
    data = ReferralRequestReadSerializer(many=True)

class HttpReferralRequestRetrieveSerializer(HttpResponeSerializer):
    """Serializer for listing referral requests"""
    data = ReferralRequestReadSerializer()


class ReferralRequestCreateSerializer(serializers.Serializer):
    """Serializer for creating referral requests"""
    pass

