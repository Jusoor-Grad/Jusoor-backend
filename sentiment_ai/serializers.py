from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from appointments.serializers import DatetimeIntervalSerializer
from authentication.models import User
from authentication.serializers import PatientMiniReadSerializer, PatientReadSerializer
from chat.chat_serializers.base import ChatMessageReadSerializer
from chat.enums import PENDING
from chat.models import ChatMessage
from core.serializers import HttpErrorResponseSerializer, HttpErrorSerializer, HttpInnerErrorSerialzier, HttpPaginatedSerializer, HttpSuccessResponseSerializer
from core.types import DatetimeInterval
from sentiment_ai.enums import COMPLETED
from sentiment_ai.models import MessageSentiment, ReportSentimentMessage, SentimentReport
from rest_framework import serializers
from drf_yasg.utils import swagger_serializer_method
from rest_framework.exceptions import ValidationError

from sentiment_ai.tasks import generate_sentiment_report



# --------------- Sentiment reports

class SentimentReportMiniReadSerializer(serializers.ModelSerializer):

    messages_covered = serializers.SerializerMethodField()
    patient = serializers.SerializerMethodField()

    def get_messages_covered(self, obj: SentimentReport):
        return ReportSentimentMessage.objects.filter(report=obj).count()
    
    @swagger_serializer_method(serializer_or_field=PatientMiniReadSerializer)
    def get_patient(self, obj: SentimentReport):
        return PatientMiniReadSerializer(obj.patient.user).data


    class Meta:
        model = SentimentReport
        fields = ['pk', 'created_at', 'sentiment_score', 'messages_covered', 'status', 'patient']

class SentimentReportRetrieveSerializer(SentimentReportMiniReadSerializer):

    messages = serializers.SerializerMethodField()

    @swagger_serializer_method(serializer_or_field=ChatMessageReadSerializer(many=True))
    def get_messages(self, obj: SentimentReport):
        return ChatMessageReadSerializer(ChatMessage.objects.filter(sentiment_result__sentiment_report__report=obj), many=True).data

    @swagger_serializer_method(serializer_or_field=PatientReadSerializer)
    def get_patient(self, obj: SentimentReport):
        return PatientReadSerializer(obj.patient.user).data

    class Meta:
        model = SentimentReport
        fields = ['pk', 'created_at', 'sentiment_score', 'messages_covered', 'status', 'patient', 'messages', 'conversation_highlights', 'recommendations', 'no_mental_disorder_score', 'depression_score', 'autism_score', 'adhd_score', 'anxiety_score', 'bipolar_score', 'ocd_score']


# TODO: change it to get the timestamp range with normal serializer

class SentimentReportCreateSerializer(DatetimeIntervalSerializer):
    patient = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(patient_profile__isnull=False), required=True)

    def create(self, validated_data):
        generate_sentiment_report.delay(validated_data['patient'].pk, start_at=validated_data['start_at'], end_at = validated_data['end_at'])
        return validated_data



# class SentimentReportCreateSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = SentimentReport
#         fields = ['patient']

#     def validate(self, attrs):
        
#         # 1. validate that the patient has more than 10 messages since
#         # his last report

#         user = self.context['request'].user

#         message_count = len(SentimentReport.get_messages_since_last_report(user))

#         print('CAPTURED MESSAGE COUNT', message_count)

#         if message_count < 10:
#             raise ValidationError(_('The patient does not have enough messages to generate a report'))

#         # 2. validate that the patient has not exceeded 3 reports per day

#         reports_today = SentimentReport.objects.filter(
#             patient=user.patient_profile, created_at__date=timezone.now().date(),
#             status__in=[PENDING, COMPLETED]
#             ).count()

#         if reports_today >= 3:
#             raise ValidationError(_('The patient has exceeded the number of reports allowed per day'))
        
#         return attrs
        

#     def create(self, validated_data):
#         generate_sentiment_report.delay(validated_data['patient'].user.pk)
#         return validated_data

#  ------------ sentiment report http schema serializers

class PagintedSentimentReportSerializer(HttpPaginatedSerializer):
    results= SentimentReportMiniReadSerializer(many=True)

class SentimentReportListHttpSerializer(HttpSuccessResponseSerializer):
    data = PagintedSentimentReportSerializer()

class SentimentReportRetrieveHttpSerializer(HttpSuccessResponseSerializer):
    data = SentimentReportRetrieveSerializer()

class SentimentReportCreateErrorSerializer(HttpInnerErrorSerialzier):
    patient = serializers.ListSerializer(child=serializers.CharField(), allow_null= True)

class SentimentReportCreateInnerErrorHttpSerializer(serializers.Serializer):
    errors = SentimentReportCreateErrorSerializer()

class SentimentReportCreateHttpSerializer(HttpErrorResponseSerializer):
    data = SentimentReportCreateInnerErrorHttpSerializer()


# --------------- Sentiment messages
    
class MessageSentimentReadSerializer(serializers.ModelSerializer):

    message = ChatMessageReadSerializer()

    class Meta:
        model = MessageSentiment
        fields = ['message', 'sad', 'joy', 'fear', 'anger']


class PaginatedMessageSentimentSerializer(HttpPaginatedSerializer):
    results = MessageSentimentReadSerializer(many=True)

class MessageSentimentListHttpSerializer(HttpSuccessResponseSerializer):
    data = PaginatedMessageSentimentSerializer()

class MessageSentimentRetrieveHttpSerializer(HttpSuccessResponseSerializer):
    data = MessageSentimentReadSerializer()