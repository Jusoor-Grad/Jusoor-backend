from authentication.permissions import IsPatient, IsTherapist
from core.enums import QuerysetBranching, UserRole
from core.querysets import OwnedQS, PatientOwnedQS, QSWrapper, TherapistOwnedQS
from core.viewssets import AugmentedViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin, CreateModelMixin
from django.utils.translation import gettext_lazy as _

from surveys.models import TherapistSurvey, TherapistSurveyQuestion, TherapistSurveyQuestionResponse, TherapistSurveyResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action

class TherapistSurveyViewset(AugmentedViewSet, ListModelMixin, RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin, CreateModelMixin):
    """
        Viewset for the TherapistSurvey model
    """

    filterset_fields = ['therapist', 'active', 'ready_to_publish', 'created_at', 'last_updated_at', 'name']
    ordering_fields = ['created_at', 'last_updated_at']
    ordering = ['-last_updated_at']


    action_permissions = {
        "list": [IsPatient() | IsTherapist()],
        "retrieve": [IsPatient() | IsTherapist()],
        "create": [IsTherapist()],
        "update": [IsTherapist()],
        "partial_update": [IsTherapist()],
        "destroy": [IsTherapist()]
    }

    serializer_class_by_action = {}

    queryset_by_action = {
        "list": TherapistSurveyQuestion.objects.all(),
        "retrieve":  TherapistSurveyQuestion.objects.all(),
        "create": QSWrapper(TherapistSurveyQuestion.objects.all()).branch(qs_mapper={UserRole.THERAPIST.value: TherapistOwnedQS(ownership_fields=['therapist'])}, by= QuerysetBranching.USER_GROUP),
        "update": QSWrapper(TherapistSurveyQuestion.objects.all()).branch(qs_mapper={UserRole.THERAPIST.value: TherapistOwnedQS(ownership_fields=['therapist'])}, by= QuerysetBranching.USER_GROUP),
        "partial_update": QSWrapper(TherapistSurveyQuestion.objects.all()).branch(qs_mapper={UserRole.THERAPIST.value: TherapistOwnedQS(ownership_fields=['therapist'])}, by= QuerysetBranching.USER_GROUP),
        "destroy": QSWrapper(TherapistSurveyQuestion.objects.all()).branch(qs_mapper={UserRole.THERAPIST.value: TherapistOwnedQS(ownership_fields=['therapist'])}, by= QuerysetBranching.USER_GROUP),
    
    
    }


    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    

class TherapistSurveyQuestionViewset(AugmentedViewSet, ListModelMixin, RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin, CreateModelMixin):
    """
        Viewset for the TherapistSurveyQuestion model
    """

    filterset_fields = ['survey', 'question_type', 'active', 'ready_to_publish', 'created_at', 'last_updated_at', 'description']

    ordering_fields = ['pk', 'created_at', 'last_updated_at']
    ordering_fields = ['pk']

    action_permissions = {
        "list": [IsPatient() | IsTherapist()],
        "retrieve": [IsPatient() | IsTherapist()],
        "create": [IsTherapist()],
        "update": [IsTherapist()],
        "partial_update": [IsTherapist()],
        "destroy": [IsTherapist()]
    }

    serializer_class_by_action = {}

    queryset_by_action = {
        "list": TherapistSurveyQuestion.objects.all(),
        "retrieve":  TherapistSurveyQuestion.objects.all(),
        "create": QSWrapper(TherapistSurveyQuestion.objects.all()).branch(qs_mapper={UserRole.THERAPIST.value: TherapistOwnedQS(ownership_fields=['survey__therapist'])}, by= QuerysetBranching.USER_GROUP),
        "update": QSWrapper(TherapistSurveyQuestion.objects.all()).branch(qs_mapper={UserRole.THERAPIST.value: TherapistOwnedQS(ownership_fields=['survey__therapist'])}, by= QuerysetBranching.USER_GROUP),
        "partial_update": QSWrapper(TherapistSurveyQuestion.objects.all()).branch(qs_mapper={UserRole.THERAPIST.value: TherapistOwnedQS(ownership_fields=['survey__therapist'])}, by= QuerysetBranching.USER_GROUP),
        "destroy": QSWrapper(TherapistSurveyQuestion.objects.all()).branch(qs_mapper={UserRole.THERAPIST.value: TherapistOwnedQS(ownership_fields=['survey__therapist'])}, by= QuerysetBranching.USER_GROUP),
    
    
    }


    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)
    
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
    
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
    
    @action('POST', detail=True, url_path=r'questions/(?<question_id>\d+)', url_name='questions')
    def answer(self, request, pk, question_id, *args, **kwargs):
        """
            answer a question on the survey
        """
        pass

    
# class TherapistSurveyQuestionResposneViewset(AugmentedViewSet, ListModelMixin, CreateModelMixin, RetrieveModelMixin):