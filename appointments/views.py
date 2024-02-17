import json
from multiprocessing import context
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from appointments.constants.enums import APPOINTMENT_STATUS_CHOICES, CANCELLED, PATIENT_FIELD, REFERRER_FIELD, REFERRER_OR_REFEREE_FIELD, UPDATEABLE_APPOINTMENT_STATI
from appointments.models import Appointment, AvailabilityTimeSlot, PatientReferralRequest
from .serializers import AppointmentCreateSerializer, AppointmentReadSerializer, AppointmentUpdateSerializer, AvailabilityTimeslotSingleUpdateSerializer, HttpAppointmentCreateSerializer, HttpAppointmentListSerializer, HttpAppointmentRetrieveSerializer, HttpAppointmentUpdateSerializer, HttpAvailabilityTimeslotUpdateSuccessResponse, ReferralRequestReadSerializer,  AvailabilityTimeslotBatchCreateSerializer, AvailabilityTimeslotBatchUploadSerializer, AvailabilityTimeslotCreateSerializer, AvailabilityTimeslotReadSerializer, HttpAvailabilityTimeslotCreateResponseSerializer, HttpAvailabilityTimeslotListSerializer, HttpAvailabilityTimeslotRetrieveSerializer, HttpErrorAvailabilityTimeslotBatchCreateResponse,  HttpReferralRequestListSerializer, HttpReferralRequestRetrieveSerializer, HttpReferralRequestUpdateResponseSerializer, ReferralRequestCreateSerializer, ReferralRequestReplySerializer, ReferralRequestUpdateSerializer, AvailabilityTimeslotBatchUpdateSerializer
from authentication.mixins import ActionBasedPermMixin
from authentication.utils import HasPerm
from core.enums import QuerysetBranching, UserRole
from core.http import Response
from core.mixins import QuerysetMapperMixin, SerializerMapperMixin
from authentication.permissions import IsPatient, IsTherapist
from core.types import DatetimeInterval, WeeklyTimeSchedule
from core.utils.time import TimeUtil
from core.viewssets import AugmentedViewSet
import rest_framework.status as status
from drf_yasg.utils import swagger_auto_schema
from core.querysets import  OwnedQS, PatientOwnedQS, QSWrapper, TherapistOwnedQS
from core.renderer import FormattedJSONRenderrer
from core.serializers import HttpErrorResponseSerializer, HttpSuccessResponeSerializer
from core.http import Response
from django.utils.translation import gettext as _

class AppointmentsViewset(AugmentedViewSet, ListModelMixin, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin):
    """View for appointments functionality"""


    ordering_fields = ['start_at']
    ordering = ['start_at']
    filterset_fields = {
        'status': ['iexact'],
        'start_at': ['gte', 'lte'],
        'timeslot__therapist': ['exact'],
    }


    action_permissions = {
        'list': [IsAuthenticated],
        'retrieve': [IsAuthenticated],
        'create': [IsAuthenticated],
        'update': [IsAuthenticated],
        'cancel': [IsAuthenticated]
       
    }
    serializer_class_by_action = {
        'list': AppointmentReadSerializer,
        'retrieve': AppointmentReadSerializer,
        'create': AppointmentCreateSerializer,
        'update': AppointmentUpdateSerializer,
    }

    queryset_by_action = {
        'list': QSWrapper(Appointment.objects.all())\
                        .branch({
                        UserRole.PATIENT.value: PatientOwnedQS(ownership_fields=[PATIENT_FIELD])
                        },
                        by=QuerysetBranching.USER_GROUP, 
                        pass_through=[UserRole.THERAPIST.value]),
        'retrieve': QSWrapper(Appointment.objects.all())\
                        .branch({
                        UserRole.PATIENT.value: PatientOwnedQS(ownership_fields=[PATIENT_FIELD])
                        },
                        by=QuerysetBranching.USER_GROUP, 
                        pass_through=[UserRole.THERAPIST.value]),
        'create': QSWrapper(Appointment.objects.all())\
                        .branch({
                        UserRole.PATIENT.value: PatientOwnedQS(ownership_fields=[PATIENT_FIELD])
                        },
                        by=QuerysetBranching.USER_GROUP, 
                        pass_through=[UserRole.THERAPIST.value]),
        # TODO: test the endpoint formally
        'update': QSWrapper(Appointment.objects.all())\
                        .branch({
                        UserRole.PATIENT.value: PatientOwnedQS(ownership_fields=[PATIENT_FIELD]),
                        UserRole.THERAPIST.value: TherapistOwnedQS(ownership_fields=['timeslot__therapist'])
                        },
                        by=QuerysetBranching.USER_GROUP, 
                        ),
        'cancel': QSWrapper(Appointment.objects.all())\
                        .branch({
                        UserRole.PATIENT.value: PatientOwnedQS(ownership_fields=['patient']),
                        UserRole.THERAPIST.value: TherapistOwnedQS(ownership_fields=['timeslot__therapist'])
                        },
                        by=QuerysetBranching.USER_GROUP, 
                        )
        
    }

    @swagger_auto_schema(responses={status.HTTP_200_OK: HttpAppointmentListSerializer()})
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(responses={status.HTTP_200_OK: HttpAppointmentRetrieveSerializer()})
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

   
    @swagger_auto_schema(responses={status.HTTP_200_OK: HttpAppointmentCreateSerializer(), status.HTTP_400_BAD_REQUEST: HttpErrorResponseSerializer()})
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(responses={status.HTTP_200_OK: HttpAppointmentUpdateSerializer(), status.HTTP_400_BAD_REQUEST: HttpErrorResponseSerializer()})
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(responses={200: HttpSuccessResponeSerializer()})    
    @action(methods=['PATCH'], detail=True)
    def cancel(self, request, *args, **kwargs):
        """
            Cancel an appointment
        """
        instance: Appointment = self.get_object()
        instance.status = CANCELLED
        instance.save()

        return Response(data=None, status=status.HTTP_200_OK, message=_('Appointment cancelled successfully'))



class AvailabilityTimeslotViewset(AugmentedViewSet, ListModelMixin, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin, DestroyModelMixin):
    """View for availability timeslot functionality"""

    ordering_fields = ['start_at']
    ordering = ['start_at']
    filterset_fields = {
        'start_at': ['gte', 'lte'],
        'therapist': ['exact']
    }
    
    action_permissions = {
        'list': [IsAuthenticated],
        'retrieve': [IsAuthenticated],
        'create': [IsTherapist()],
        'batch_create': [IsTherapist()],
        'update': [IsTherapist()],
        'batch_update': [IsTherapist()],
        'destroy': [IsTherapist()]       
    }

    serializer_class_by_action = {
        'list': AvailabilityTimeslotReadSerializer ,
        'retrieve': AvailabilityTimeslotReadSerializer,
        'create': AvailabilityTimeslotCreateSerializer,
        'batch_create': AvailabilityTimeslotBatchCreateSerializer,
        'update': AvailabilityTimeslotSingleUpdateSerializer,
        'batch_update': AvailabilityTimeslotBatchUpdateSerializer,
    }

    queryset_by_action = {
        'list': AvailabilityTimeSlot.objects.all().select_related('therapist__user'),
        'retrieve': AvailabilityTimeSlot.objects.all().select_related('therapist__user'),
        'update': QSWrapper(AvailabilityTimeSlot.objects.all())
                    .branch({
                        UserRole.THERAPIST.value: TherapistOwnedQS()
                        },
                        by=QuerysetBranching.USER_GROUP, 
                        pass_through=[UserRole.THERAPIST.value]),
        'batch_update': QSWrapper(AvailabilityTimeSlot.objects.all())
                        .branch({
                            UserRole.THERAPIST.value: TherapistOwnedQS()
                            },
                            by=QuerysetBranching.USER_GROUP)
    }
   
    
    @swagger_auto_schema(responses={200: HttpAvailabilityTimeslotListSerializer()})
    def list(self, request, *args, **kwargs):
        return (super().list(request, *args, **kwargs))

   
    
    @swagger_auto_schema(responses={200: HttpAvailabilityTimeslotRetrieveSerializer()})
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

   
    @swagger_auto_schema(responses={200: HttpAvailabilityTimeslotCreateResponseSerializer(), status.HTTP_400_BAD_REQUEST: HttpErrorAvailabilityTimeslotBatchCreateResponse()})
    def create(self, request, *args, **kwargs):
        """
            Creates one or more availability timeslots with no recurrcne

             **@validation**:
                - all passed time intervals must not conflict with each other
                - the schedule created from the specified intervals must not conflict with any existing timeslots
        """
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(responses={200: None, status.HTTP_400_BAD_REQUEST: HttpErrorAvailabilityTimeslotBatchCreateResponse()})
    @action(methods=['POST'], detail=False)
    def batch_create(self, request, *args, **kwargs):
        """
            Createing a group of timeslots by specifiyng a weekly schedule with multiple time intervals along a date span

            **@validation**:
                - all passed time intervals must not conflict with each other
                - the schedule created from the specified intervals must not conflict with any existing timeslots
        """
        
        # 1. raw data validation
        serializer = AvailabilityTimeslotBatchUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        # 2. generate all matching datetime intervals using rrules
        intervals = TimeUtil.generate_intervals(WeeklyTimeSchedule(**data['weekly_schedule']), DatetimeInterval(start_at=data['start_at'], end_at=data['end_at']))
        # 3. validate the generated data using the create serializer
        conflict_serializer = AvailabilityTimeslotBatchCreateSerializer(data={
            'weekly_schedule': intervals,
            'start_at': data['start_at'],
            'end_at': data['end_at'],
           
        }, context=self.get_serializer_context())
        conflict_serializer.is_valid(raise_exception=True)

        # 4. create the timeslots if valid
        self.perform_create(conflict_serializer)

        return Response(data=conflict_serializer.data, status=status.HTTP_201_CREATED)
    
    @swagger_auto_schema(responses={200: HttpAvailabilityTimeslotUpdateSuccessResponse(), 400: HttpAvailabilityTimeslotUpdateSuccessResponse()})
    @action(
        methods=['PUT'],
        detail=True,
    )
    def batch_update(self, request, *args, **kwargs):

        instance = self.get_object()
        serializer = self.get_serializer(instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        print('Hello?')
        self.perform_update(serializer)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(responses={200: HttpAvailabilityTimeslotUpdateSuccessResponse(), 400: HttpReferralRequestUpdateResponseSerializer()})
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    



class ReferralViewset(ActionBasedPermMixin, SerializerMapperMixin, QuerysetMapperMixin, GenericViewSet, ListModelMixin, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin):
    """View for referral functionality"""

    renderer_classes = [FormattedJSONRenderrer]

    ordering_fields = ['created_at']
    ordering = ['created_at']
    filterset_fields = {
        'status': ['iexact'],
        'referrer': ['exact'],
        'referee': ['exact']
    }
    
    action_permissions = {
        'list': [IsAuthenticated],
        'retrieve': [IsAuthenticated],
        'create': [IsAuthenticated],
        'update': [IsPatient()],
        'partial_update': [IsPatient()],
        'reply': [IsTherapist()]
    }
    serializer_class_by_action = {
        'list': ReferralRequestReadSerializer,
        'retrieve': ReferralRequestReadSerializer,
        'create': ReferralRequestCreateSerializer,
        'update': ReferralRequestUpdateSerializer,
        'partial_update': ReferralRequestUpdateSerializer,
        'reply': ReferralRequestReplySerializer
    }

    queryset_by_action = {
        'list': QSWrapper(PatientReferralRequest.objects.all().select_related('responding_therapist__user'))
                    .branch({
                        UserRole.PATIENT.value: OwnedQS(ownership_fields=REFERRER_OR_REFEREE_FIELD)
                        },
                        by=QuerysetBranching.USER_GROUP, 
                        pass_through=[UserRole.THERAPIST.value]),
        'retrieve': QSWrapper(PatientReferralRequest.objects.all().select_related('responding_therapist__user'))
                    .branch({
                        UserRole.PATIENT.value: OwnedQS(ownership_fields=REFERRER_OR_REFEREE_FIELD)
                        },
                        by=QuerysetBranching.USER_GROUP, 
                        pass_through=[UserRole.THERAPIST.value]),
        'update': QSWrapper(PatientReferralRequest.objects.all())
                    .branch({
                        UserRole.PATIENT.value: OwnedQS(ownership_fields=[REFERRER_FIELD])
                        },
                        by=QuerysetBranching.USER_GROUP, 
                        pass_through=[UserRole.THERAPIST.value]),
        'partial_update': QSWrapper(PatientReferralRequest.objects.all())
                    .branch({
                        UserRole.PATIENT.value: OwnedQS(ownership_fields=[REFERRER_FIELD])
                        },
                        by=QuerysetBranching.USER_GROUP, 
                        pass_through=[UserRole.THERAPIST.value]),
        'reply': PatientReferralRequest.objects.filter(status='PENDING')
    }

   
    # TODO: filters by status
    @swagger_auto_schema(responses={200: HttpReferralRequestListSerializer()})
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

   
    @swagger_auto_schema(responses={200: HttpReferralRequestRetrieveSerializer()})
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

   
    @swagger_auto_schema(responses={200: HttpReferralRequestRetrieveSerializer()})
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

   
    @swagger_auto_schema(responses={200: HttpReferralRequestUpdateResponseSerializer()})
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(responses={200: HttpReferralRequestUpdateResponseSerializer(partial=True)})
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(responses={200: HttpReferralRequestUpdateResponseSerializer()})    
    @action(methods=['PATCH'], detail=True)
    def reply(self, request, *args, **kwargs):
        """
            A therapist reply to a referral request 
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        
        self.perform_update(serializer)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

