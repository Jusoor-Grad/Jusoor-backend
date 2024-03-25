from authentication.permissions import IsPatient, IsTherapist
from core.enums import QuerysetBranching, UserRole
from core.models import Therapist
from core.querysets import OwnedQS, PatientOwnedQS, QSWrapper, TherapistOwnedQS
from core.serializers import HttpErrorResponseSerializer, HttpSuccessResponseSerializer
from core.viewssets import AugmentedViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin, CreateModelMixin
from django.utils.translation import gettext_lazy as _
from rest_framework.response import Response
from surveys.models import TherapistSurvey, TherapistSurveyQuestion, TherapistSurveyQuestionResponse, TherapistSurveyResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from surveys.serializers.base import TherapistSurveyMiniReadSerializer, TherapistSurveyFullReadSerializer, TherapistSurveyQuestionFullReadSerializer, TherapistSurveyQuestionMCQCreateSerializer, TherapistSurveyQuestionMiniReadSerializer, TherapistSurveyQuestionTextCreateSerializer, TherapistSurveyWriteSerializer
from surveys.serializers.http import TherapistSurveyInnerListHttpSerializer, TherapistSurveyRetrieveHttpSerializer, TherapistSurveyWriteErrorHttpSerializer, TherapistSurveyWriteSuccessHttpSerializer

class TherapistSurveyViewset(AugmentedViewSet, ListModelMixin, RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin, CreateModelMixin):
    """
        Viewset for the TherapistSurvey model
    """

    filterset_fields = ['created_by', 'last_updated_by', 'active', 'created_at', 'last_updated_at']
    ordering_fields = ['created_at', 'last_updated_at']
    ordering = ['-last_updated_at']

    # TODO: add reorder endpoint for surveys' questions
    action_permissions = {
        "list": [IsPatient() | IsTherapist()],
        "retrieve": [IsPatient() | IsTherapist()],
        "create": [IsTherapist()],
        "update": [IsTherapist()],
        "partial_update": [IsTherapist()],
        "destroy": [IsTherapist()],
        "publish": [IsTherapist()],
        "hide": [IsTherapist()],
    }

    serializer_class_by_action = {
        "list": TherapistSurveyMiniReadSerializer,
        "retrieve": TherapistSurveyFullReadSerializer,
        "create": TherapistSurveyWriteSerializer,
        "update": TherapistSurveyWriteSerializer,
        "partial_update": TherapistSurveyWriteSerializer
    }

    queryset= TherapistSurvey.objects.all()

    @swagger_auto_schema(responses={200: TherapistSurveyInnerListHttpSerializer()})
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(responses={200: TherapistSurveyRetrieveHttpSerializer()})
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(responses={200: TherapistSurveyWriteSuccessHttpSerializer(), 400: TherapistSurveyWriteErrorHttpSerializer()})
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(responses={200: TherapistSurveyWriteSuccessHttpSerializer(), 400: TherapistSurveyWriteErrorHttpSerializer()})
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
    @swagger_auto_schema({200: HttpSuccessResponseSerializer(), 400: HttpErrorResponseSerializer()})
    @action(methods=['PATCH'], detail=True, url_path='publish')
    def publish(self, request, pk, *args, **kwargs):
        """
            publish the survey
        """
        
        survey: TherapistSurvey = self.get_object()

        if survey.active:
            raise ValidationError(_("Survey already active"))
        elif survey.questions.filter(active=True).count() == 0:
            raise ValidationError(_("Survey has no questions to publish"))
        else:
            survey.active = True
            return Response({"message": _("survey activated successfully")}, status=200)
            

    @swagger_auto_schema({200: HttpSuccessResponseSerializer(), 400: HttpErrorResponseSerializer()})
    @action(methods=['PATCH'], detail=True, url_path='hide')
    def hide(self, request, pk, *args, **kwargs):
        """
            hide the survey
        """
        
        survey: TherapistSurvey = self.get_object()

        if not survey.active:
            raise ValidationError(_("Survey already hidden"))
        
        else:
            survey.active = False
            return Response({"message": _("survey hidden successfully")}, status=200)
    
    @swagger_auto_schema(responses={200: TherapistSurveyWriteSuccessHttpSerializer(), 400: TherapistSurveyWriteErrorHttpSerializer()})
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

class TherapistSurveyQuestionViewset(AugmentedViewSet, ListModelMixin, RetrieveModelMixin, DestroyModelMixin):
    """
        Viewset for the TherapistSurveyQuestion model
    """

    filterset_fields = ['survey', 'question_type', 'active', 'created_at', 'last_updated_at', 'description']

    ordering_fields = ['pk', 'created_at', 'last_updated_at']
    ordering_fields = ['pk']

    action_permissions = {
        "list": [IsPatient() | IsTherapist()],
        "retrieve": [IsPatient() | IsTherapist()],
        "create_mc_question": [IsTherapist()],
        "create_text_question": [IsTherapist()],
        "update_mc_question": [IsTherapist()],
        "update_text_question": [IsTherapist()],
        "publish": [IsTherapist()],
        "hide": [IsTherapist()],
        "partial_update": [IsTherapist()],
        "destroy": [IsTherapist()]
    }

    serializer_class_by_action = {
        "list": TherapistSurveyQuestionMiniReadSerializer,
        "retrieve": TherapistSurveyQuestionFullReadSerializer,
        "create_mc_question": TherapistSurveyQuestionMCQCreateSerializer,
        "create_text_question": TherapistSurveyQuestionTextCreateSerializer,
        "update_mc_question": TherapistSurveyQuestionMCQCreateSerializer,
    }

    queryset = TherapistSurveyQuestion.objects.all()


    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @action('POST', detail=False, url_path='text', url_name='text')
    def create_text_question(self, request, *args, **kwargs):
        # return super().create(request, *args, **kwargs)
        pass
    
    @action('POST', detail=False, url_path='mcq', url_name='mcq')
    def create_mc_question(self, request, *args, **kwargs):
        # return super().create(request, *args, **kwargs)
        pass
    
    @action('PUT', detail=False, url_path='text', url_name='text')
    def update_text_question(self, request, *args, **kwargs):
        # return super().update(request, *args, **kwargs)
        pass
    
    @action('PUT', detail=False, url_path='mcq', url_name='mcq')
    def update_mc_question(self, request, *args, **kwargs):
        # return super().update(request, *args, **kwargs)
        pass

    # TODO: question ordering should be preserved when deleting a question
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


    @swagger_auto_schema({200: HttpSuccessResponseSerializer(), 400: HttpErrorResponseSerializer()})
    @action('PATCH', detail=True, url_path='publish', url_name='publish')
    def publish(self, request, pk, *args, **kwargs):
        """
            publish the survey question
        """
        
        survey_question: TherapistSurveyQuestion = self.get_object()

        if survey_question.active:
            raise ValidationError(_("Survey question already active"))
        else:
            survey_question.active = False
            return Response({"message": _("Survey question activated successfully")}, status=200)
            

    @swagger_auto_schema({200: HttpSuccessResponseSerializer(), 400: HttpErrorResponseSerializer()})
    @action('PATCH', detail=True, url_path='hide', url_name='hide')
    def hide(self, request, pk, *args, **kwargs):
        """
            hide the survey question
        """
        
        survey_question: TherapistSurveyQuestion = self.get_object()

        if not survey_question.active:
            raise ValidationError(_("Survey question already hidden"))
        
        else:
            survey_question.active = False
            return Response({"message": _("Survey question hidden successfully")}, status=200)
    
class TherapistSurveyResponseViewset(AugmentedViewSet, ListModelMixin, CreateModelMixin, RetrieveModelMixin):
    """
        Viewset for the TherapistSurveyResponse model
    """

    filterset_fields = ['survey', 'patient', 'status', 'created_at', 'last_updated_at']

    ordering_fields = ['pk', 'created_at', 'last_updated_at']
    ordering_fields = ['-created_at']

    action_permissions = {
        "list": [IsPatient() | IsTherapist()],
        "retrieve": [IsPatient() | IsTherapist()],
        "create": [IsPatient()],
    }

    serializer_class_by_action = {}

    queryset_by_action = {
        "list": QSWrapper(TherapistSurveyResponse.objects.all()).branch(qs_mapper={
            UserRole.PATIENT.value: PatientOwnedQS(ownership_fields=['patient'])
            },pass_through=[IsTherapist()], by= QuerysetBranching.USER_GROUP),
        "retrieve": QSWrapper(TherapistSurveyResponse.objects.all()).branch(qs_mapper={
            UserRole.PATIENT.value: PatientOwnedQS(ownership_fields=['patient'])
            },pass_through=[IsTherapist()], by= QuerysetBranching.USER_GROUP),
        "create": QSWrapper(TherapistSurveyResponse.objects.all()).branch(qs_mapper={
            UserRole.PATIENT.value: PatientOwnedQS(ownership_fields=['patient'])
            },pass_through=[IsTherapist()], by= QuerysetBranching.USER_GROUP),
           
        }
        
    


    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    @action('POST', detail=True, url_path=r'questions/(?P<question_id>\d+)', url_name='questions')
    def answer(self, request, pk, question_id, *args, **kwargs):
        """
            answer a question on the survey
        """
        pass

    
# class TherapistSurveyQuestionResposneViewset(AugmentedViewSet, ListModelMixin, CreateModelMixin, RetrieveModelMixin):