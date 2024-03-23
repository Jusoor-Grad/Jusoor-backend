

from core.serializers import HttpErrorResponseSerializer, HttpErrorSerializer, HttpPaginatedSerializer, HttpSuccessResponseSerializer
from surveys.serializers.base import TherapistSurveyMiniReadSerializer, TherapistSurveyFullReadSerializer, TherapistSurveyWriteSerializer
from rest_framework import serializers

class TherapistSurveyRetrieveHttpSerializer(HttpSuccessResponseSerializer):
    data = TherapistSurveyFullReadSerializer()

class TherapistSurveyInnerListHttpSerializer(HttpPaginatedSerializer):
    results = TherapistSurveyMiniReadSerializer(many=True)

class TherapistSurveyListHttpSerializer(HttpSuccessResponseSerializer):
    data = TherapistSurveyInnerListHttpSerializer()

class TherapistSurveyWriteSuccessHttpSerializer(HttpSuccessResponseSerializer):
    data = TherapistSurveyWriteSerializer()

class TherapistSurveyWriteErrorWrapperHttpSerializer(serializers.Serializer):
    name = serializers.ListSerializer(child=serializers.CharField())
    image = serializers.ListSerializer(child=serializers.CharField())

class TherapistSurveyWriteErrorHttpSerializer(HttpErrorResponseSerializer):
    data = TherapistSurveyWriteErrorWrapperHttpSerializer()