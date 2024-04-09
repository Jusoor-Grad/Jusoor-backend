from django.db import transaction
from django.db.models import Q
from appointments.constants.enums import PENDING_THERAPIST
from appointments.models import Appointment, AppointmentSurveyResponse
from authentication.permissions import IsPatient, IsTherapist
from core.enums import QuerysetBranching, UserRole
from core.querysets import PatientOwnedQS, QSWrapper
from core.serializers import HttpErrorResponseSerializer, HttpSuccessResponseSerializer
from core.viewssets import AugmentedViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin, CreateModelMixin
from django.utils.translation import gettext_lazy as _
from rest_framework.response import Response
from surveys.enums import COMPLETED, SurveyQuestionTypes
from surveys.models import TherapistSurvey, TherapistSurveyQuestion, TherapistSurveyResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from surveys.serializers.base import TherapistSurveyMCQUpdateSerializer, TherapistSurveyMiniReadSerializer, TherapistSurveyFullReadSerializer, TherapistSurveyQuestionFullReadSerializer, TherapistSurveyQuestionImageUploadSerializer, TherapistSurveyQuestionMCQCreateSerializer, TherapistSurveyQuestionMCQResponseSerializer, TherapistSurveyQuestionMiniReadSerializer, TherapistSurveyQuestionTextCreateSerializer, TherapistSurveyQuestionTextResponseSerializer, TherapistSurveyResponseCreateSerializer, TherapistSurveyTextUpdateSerializer, TherapistSurveyWriteSerializer, ThreapistSurveyResponseFullReadSerializer, ThreapistSurveyResponseMiniReadSerializer
from surveys.serializers.http import TherapistSurveyInnerListHttpSerializer, TherapistSurveyQuestionUpdateHttpErrorSerializer, TherapistSurveyQuestionUpdateMCQHttpSerializer, TherapistSurveyQuestionCreateHttpErrorSerializer, TherapistSurveyQuestionCreateMCQHttpSerializer, TherapistSurveyQuestionCreateTextHttpSerializer, TherapistSurveyQuestionListHttpSerializer, TherapistSurveyQuestionRetireveMCQHttpSerializer, TherapistSurveyQuestionRetrieveTextHttpSerializer, TherapistSurveyQuestionUpdateTextHttpSerializer, TherapistSurveyResponseAnswerErrorSerializer, TherapistSurveyResponseAnswerHttpErrorResposneSerializer, TherapistSurveyResponseCreateHttpErrorSerializer, TherapistSurveyResponseCreateHttpSerializer, TherapistSurveyResponseListHttpSerializer, TherapistSurveyResponseMCQAnswerHttpSuccessSerializer, TherapistSurveyResponseRetrieveHttpSerializer, TherapistSurveyRetrieveHttpSerializer, TherapistSurveyWriteErrorHttpSerializer, TherapistSurveyWriteSuccessHttpSerializer
from drf_yasg import openapi
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
            survey.save()
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
            survey.save()
            return Response({"message": _("survey hidden successfully")}, status=200)
    
    @swagger_auto_schema(responses={200: TherapistSurveyWriteSuccessHttpSerializer(), 400: TherapistSurveyWriteErrorHttpSerializer()})
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

class TherapistSurveyQuestionViewset(AugmentedViewSet, ListModelMixin, DestroyModelMixin):
    """
        Viewset for the TherapistSurveyQuestion model
    """

    filterset_fields = {
        'survey': ['exact'],
        'active': ['exact'],
        'created_at': ['exact', 'lt', 'gt'],
        'last_updated_at': ['exact', 'lt', 'gt'],
        "question_type": ["iexact"],
        "description": ["icontains"],
    }

    ordering_fields = ['pk', 'created_at', 'last_updated_at']
    ordering_fields = ['pk']

    action_permissions = {
        "list": [IsPatient() | IsTherapist()],
        "retrieve_mc_question": [IsPatient() | IsTherapist()],
        "retrieve_text_question": [IsPatient() | IsTherapist()],
        "create_mc_question": [IsTherapist()],
        "create_text_question": [IsTherapist()],
        "update_mc_question": [IsTherapist()],
        "update_text_question": [IsTherapist()],
        "upload_image": [IsTherapist()],
        "publish": [IsTherapist()],
        "hide": [IsTherapist()],
        "destroy": [IsTherapist()]
    }

    serializer_class_by_action = {
        "list": TherapistSurveyQuestionMiniReadSerializer,
        "retrieve_mc_question": TherapistSurveyQuestionFullReadSerializer,
        "retrieve_text_question": TherapistSurveyQuestionFullReadSerializer,
        "create_mc_question": TherapistSurveyQuestionMCQCreateSerializer,
        "create_text_question": TherapistSurveyQuestionTextCreateSerializer,
        "update_mc_question": TherapistSurveyMCQUpdateSerializer,
        "update_text_question": TherapistSurveyTextUpdateSerializer,
        "upload_image": TherapistSurveyQuestionImageUploadSerializer,

    }

    # TODO: only show active questions to patients
    queryset_by_action = {
        "list": TherapistSurveyQuestion.objects.all(),
        "retrieve_text_question": QSWrapper(TherapistSurveyQuestion.objects.filter(question_type=SurveyQuestionTypes.TEXT.value)).branch(qs_mapper={
            UserRole.PATIENT.value: Q(active=True)
        },
        pass_through=[UserRole.THERAPIST.value], by= QuerysetBranching.USER_GROUP),
        "update_text_question": TherapistSurveyQuestion.objects.filter(question_type=SurveyQuestionTypes.TEXT.value),
        "retrieve_mc_question": QSWrapper(TherapistSurveyQuestion.objects.filter(question_type=SurveyQuestionTypes.MULTIPLE_CHOICE.value)).branch(qs_mapper={
            UserRole.PATIENT.value: Q(active=True)
        },
        pass_through=[UserRole.THERAPIST.value], by= QuerysetBranching.USER_GROUP),
        "update_mc_question": TherapistSurveyQuestion.objects.filter(question_type=SurveyQuestionTypes.MULTIPLE_CHOICE.value),
        "publish": TherapistSurveyQuestion.objects.all(),
        "upload_image": TherapistSurveyQuestion.objects.all(),
        "hide": TherapistSurveyQuestion.objects.all(),
        "destroy": TherapistSurveyQuestion.objects.all(),
    }

    @swagger_auto_schema(responses={200: TherapistSurveyQuestionListHttpSerializer()})
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @action(['POST'], detail=True, url_path='upload-image', url_name='upload-image')
    def upload_image(self, request, *args, **kwargs):
        
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    
    @swagger_auto_schema(responses={200: TherapistSurveyQuestionRetireveMCQHttpSerializer()})
    @action(['GET'], detail=True, url_path='mcq', url_name='mcq')
    def retrieve_mc_question(self, request, *args, **kwargs):
        
        instance = self.get_object()
        return Response(self.get_serializer(instance).data)

    @swagger_auto_schema(responses={200: TherapistSurveyQuestionRetrieveTextHttpSerializer()})
    @action(['GET'], detail=True, url_path='text', url_name='text')
    def retrieve_text_question(self, request, *args, **kwargs):
        instance = self.get_object()
        return Response(self.get_serializer(instance).data)
    
    @swagger_auto_schema(responses={201: TherapistSurveyQuestionCreateTextHttpSerializer(), 400: TherapistSurveyQuestionCreateHttpErrorSerializer()})
    @action(['POST'], detail=False, url_path='text', url_name='text')
    def create_text_question(self, request, *args, **kwargs):
        """ Create a new text question

        .
        
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=201)    

    
    @swagger_auto_schema(responses={201: TherapistSurveyQuestionCreateMCQHttpSerializer(), 400: TherapistSurveyQuestionCreateHttpErrorSerializer()})
    @action(['POST'], detail=False, url_path='mcq', url_name='mcq')
    def create_mc_question(self, request, *args, **kwargs):
        """Create a new MCQ question

            .
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=201)
    
    
    @swagger_auto_schema(responses={200: TherapistSurveyQuestionUpdateTextHttpSerializer(), 400: TherapistSurveyQuestionUpdateHttpErrorSerializer()})
    @action(['PUT'], detail=True, url_path='text', url_name='text')
    def update_text_question(self, request, *args, **kwargs):
        # return super().update(request, *args, **kwargs)
        serializer = self.get_serializer(data=request.data, instance=self.get_object())
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
    
    @swagger_auto_schema(responses={200: TherapistSurveyQuestionUpdateMCQHttpSerializer(), 400: TherapistSurveyQuestionUpdateMCQHttpSerializer()})
    @action(['PUT'], detail=True, url_path='mcq', url_name='mcq')
    def update_mc_question(self, request, *args, **kwargs):
        
        serializer = self.get_serializer(data=request.data, instance=self.get_object())
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

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
            survey_question.active = True
            survey_question.save()
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
            survey_question.save()
            return Response({"message": _("Survey question hidden successfully")}, status=200)
    
class TherapistSurveyResponseViewset(AugmentedViewSet, ListModelMixin, CreateModelMixin, RetrieveModelMixin):
    """
        Viewset for the TherapistSurveyResponse model
    """

    filterset_fields = {
        'patient': ['exact'],
        'survey': ['exact'],
        'status': ['iexact'],
        'created_at': ['exact', 'lt', 'gt'],
        'last_updated_at': ['exact', 'lt', 'gt'],
    }

    ordering_fields = ['pk', 'created_at', 'last_updated_at']
    ordering_fields = ['-created_at']

    action_permissions = {
        "list": [IsPatient() | IsTherapist()],
        "retrieve": [IsPatient() | IsTherapist()],
        "create": [IsPatient()],
        "answer_mc_question": [IsPatient()],
        "answer_text_question": [IsPatient()],
        'submit': [IsPatient()],
    }

    serializer_class_by_action = {
        "list": ThreapistSurveyResponseMiniReadSerializer,
        "retrieve": ThreapistSurveyResponseFullReadSerializer,
        "create": TherapistSurveyResponseCreateSerializer,
        "answer_mc_question": TherapistSurveyQuestionMCQResponseSerializer,
        "answer_text_question": TherapistSurveyQuestionTextResponseSerializer,
        
    }

    queryset_by_action = {
        "list": QSWrapper(TherapistSurveyResponse.objects.all()).branch(qs_mapper={
            UserRole.PATIENT.value: PatientOwnedQS(ownership_fields=['patient'])
            },pass_through=[UserRole.THERAPIST.value], by= QuerysetBranching.USER_GROUP),
        "retrieve": QSWrapper(TherapistSurveyResponse.objects.all().prefetch_related('response_answers__question')).branch(qs_mapper={
            UserRole.PATIENT.value: PatientOwnedQS(ownership_fields=['patient'])
            },pass_through=[UserRole.THERAPIST.value], by= QuerysetBranching.USER_GROUP),
        "answer_mc_question": QSWrapper(TherapistSurveyResponse.objects.all()).branch(qs_mapper={
            UserRole.PATIENT.value: PatientOwnedQS(ownership_fields=['patient'])
            },pass_through=[UserRole.THERAPIST.value], by= QuerysetBranching.USER_GROUP),
        "answer_text_question": QSWrapper(TherapistSurveyResponse.objects.all()).branch(qs_mapper={
            UserRole.PATIENT.value: PatientOwnedQS(ownership_fields=['patient'])
            },pass_through=[UserRole.THERAPIST.value], by= QuerysetBranching.USER_GROUP),
        'submit': QSWrapper(TherapistSurveyResponse.objects.all()).branch(qs_mapper={
            UserRole.PATIENT.value: PatientOwnedQS(ownership_fields=['patient'])
            },pass_through=[UserRole.THERAPIST.value], by= QuerysetBranching.USER_GROUP),
        }
        
    

    @swagger_auto_schema(responses={200: TherapistSurveyResponseListHttpSerializer()})
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(responses={200: TherapistSurveyResponseRetrieveHttpSerializer()})
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(responses={200: TherapistSurveyResponseCreateHttpSerializer(), 400: TherapistSurveyResponseCreateHttpErrorSerializer()})
    def create(self, request, *args, **kwargs):

        request.data['patient'] = request.user.patient_profile.id
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(request_body = openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['answer'],
            properties={
                'answer': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_INTEGER)),
            }
    ), responses={200: TherapistSurveyResponseMCQAnswerHttpSuccessSerializer(), 400: TherapistSurveyResponseAnswerHttpErrorResposneSerializer()})
    @action(methods=['POST'], detail=True, url_path=r'mcq/(?P<question_id>\d+)', url_name='answer-mcq-q')
    def answer_mc_question(self, request, pk, question_id, *args, **kwargs):
        """
            answer an mcq question on the survey
        """

        survey_resposne: TherapistSurveyResponse = self.get_object()

        serializer = self.get_serializer(data={**request.data, 'question': question_id, 'survey_response': survey_resposne.id})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    @swagger_auto_schema(request_body = openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['answer'],
            properties={
                'answer': openapi.Schema(type=openapi.TYPE_STRING,),
            }
    ), responses={200: TherapistSurveyResponseMCQAnswerHttpSuccessSerializer(), 400: TherapistSurveyResponseAnswerHttpErrorResposneSerializer()})
    @action(['POST'], detail=True, url_path=r'text/(?P<question_id>\d+)', url_name='answer-text-q')
    def answer_text_question(self, request, pk, question_id, *args, **kwargs):
        """
            answer a text question on the survey
        """

        survey_resposne: TherapistSurveyResponse = self.get_object()

        serializer = self.get_serializer(data={**request.data, 'question': question_id, 'survey_response': survey_resposne.id})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    @swagger_auto_schema(responses={200: HttpSuccessResponseSerializer(), 400: HttpErrorResponseSerializer()})
    @transaction.atomic
    @action(['PUT'], detail=True, url_path='submit', url_name='submit')
    def submit(self, request, *args, **kwargs):
        """
            submit the survey response
        """
        
        survey_response: TherapistSurveyResponse = self.get_object()

        if survey_response.status == COMPLETED:
            raise ValidationError(_("Survey response already submitted"))
        
        # security side-info: using scoped survey resposne, we make sure that all question responses to this survey
        # also originate from the same user 
        elif survey_response.response_answers.count() != survey_response.survey.questions.filter(active=True).count():
            raise ValidationError(_("Survey response has not been fully answered"))
        else:
            # update the response object
            survey_response.status = COMPLETED

            # if there exists an appointment linked to this survey, update the status
            appointment_survey_response = AppointmentSurveyResponse.objects.filter(survey_response=survey_response).first()
            if appointment_survey_response != None:
                appointment_survey_response.appointment.status = PENDING_THERAPIST
                appointment_survey_response.appointment.save()
                
            survey_response.save()

            return Response({"message": _("Survey response submitted successfully")}, status=200)
    
# class TherapistSurveyQuestionResposneViewset(AugmentedViewSet, ListModelMixin, CreateModelMixin, RetrieveModelMixin):