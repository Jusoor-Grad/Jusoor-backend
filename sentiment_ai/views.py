from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from authentication.permissions import IsPatient, IsTherapist
from chat.agents import ChatGPTAgent
from core.enums import QuerysetBranching, UserRole
from core.querysets import PatientOwnedQS, QSWrapper
from core.serializers import HttpSuccessResponseSerializer
from core.viewssets import AugmentedViewSet
from django.utils.translation import gettext_lazy as _
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin
from rest_framework.response import Response
from sentiment_ai.agents.emotion_detector import EmotionDetector
from sentiment_ai.agents.mental_disorder_detector import MentalDisorderDetector
from sentiment_ai.models import MessageSentiment, SentimentReport
from sentiment_ai.serializers import MessageSentimentListHttpSerializer, MessageSentimentReadSerializer, SentimentReportCreateHttpSerializer, SentimentReportCreateSerializer, SentimentReportListHttpSerializer, SentimentReportMiniReadSerializer, SentimentReportRetrieveSerializer, TextScoringHttpSerializer


class SentimentReportViewset(AugmentedViewSet, ListModelMixin, RetrieveModelMixin, CreateModelMixin):
    

    
    action_permissions = {
        'list': [IsTherapist()],
        'retrieve': [IsTherapist()],
        'create': [IsTherapist()],
        
    }
    
    serializer_class_by_action = {
        'list': SentimentReportMiniReadSerializer,
        'retrieve': SentimentReportRetrieveSerializer,
        'create': SentimentReportCreateSerializer
    }

    filterset_fields = {
        'status': ['iexact'],
        'created_at': ['gte', 'lte'],
        'patient__user': ['exact'],
        'sentiment_score': ['gt', 'lt'],
    }

    ordering_fields = ['created_at', 'sentiment_score']

    queryset_by_action = {
        'list': QSWrapper(SentimentReport.objects.all().select_related('patient__user', 'patient__department')).branch(
            {
                UserRole.PATIENT.value: PatientOwnedQS()
            }, by= QuerysetBranching.USER_GROUP,
            pass_through= [UserRole.THERAPIST.value]
        ),
        'retrieve': QSWrapper(SentimentReport.objects.all().select_related('patient__user', 'patient__department')).branch(
            {
                UserRole.PATIENT.value: PatientOwnedQS()
            }, by= QuerysetBranching.USER_GROUP,
            pass_through= [UserRole.THERAPIST.value]
        ),
    }

    @swagger_auto_schema(responses={200: SentimentReportListHttpSerializer })
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    

    @swagger_auto_schema(responses={200: SentimentReportRetrieveSerializer })
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(responses={201: HttpSuccessResponseSerializer, 400: SentimentReportCreateHttpSerializer }, request_body=openapi.Schema(type=openapi.TYPE_OBJECT, description="This endpoint does not require any request body payload"))
    def create(self, request, *args, **kwargs):
        
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()        

        return Response({'message':_("Report created successfully")}, status=201)


class MessageSentimentViewset(AugmentedViewSet, ListModelMixin, RetrieveModelMixin):
    
    action_permissions = {
        'list': [IsPatient() | IsTherapist()],
        'retrieve': [IsPatient() | IsTherapist()],
        'score_text': [IsTherapist()],
    }


    serializer_class = MessageSentimentReadSerializer

    queryset_by_action = {
        'list': QSWrapper(MessageSentiment.objects.all().select_related('message__sender', 'message__receiver')).branch(
            {
                UserRole.PATIENT.value: PatientOwnedQS()
            }, by= QuerysetBranching.USER_GROUP,
            pass_through= [UserRole.THERAPIST.value]
        ),
        'retrieve': QSWrapper(MessageSentiment.objects.all().select_related('message__sender', 'message__receiver')).branch(
            {
                UserRole.PATIENT.value: PatientOwnedQS()
            }, by= QuerysetBranching.USER_GROUP,
            pass_through= [UserRole.THERAPIST.value]
        )
    }
    

    ordering_fields = ['created_at']
    filterset_fields = {
        'created_at': ['gte', 'lte'],
        'message__sender': ['exact'],
        'message__receiver': ['exact'],
        'sad': ['gt', 'lt'],
        'joy': ['gt', 'lt'],
        'fear': ['gt', 'lt'],
        'anger': ['gt', 'lt'],
        'message__id': ['exact', 'in'],
    }

    @swagger_auto_schema(responses={200: MessageSentimentListHttpSerializer() })
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    

    @swagger_auto_schema(responses={200: MessageSentimentReadSerializer() })
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(responses={200: TextScoringHttpSerializer()}, request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={'text': openapi.Schema(type=openapi.TYPE_STRING, description="The text to be scored")}))
    @action(methods=['post'], detail=False, url_path='score-text', url_name='score-text')
    def score_text(self, request, *args, **kwargs):

        data = request.data.get('text', None)

        if not type(data) == str:
            return Response({'message':_("Invalid data type")}, status=400)

        emotion = EmotionDetector().predict_from_text(data)

        mental_disorders = MentalDisorderDetector().predict(data)

        relevant_message = ChatGPTAgent().get_relevant_docs(data)[0]

        return Response({
            'emotion': emotion.model_dump(),
            'mental_disorders': mental_disorders.model_dump(),
            'relevant_conversation': {
                'patient_message': relevant_message.page_content,
                'therapist_message': relevant_message.metadata['response']
            }
        }, status=200)