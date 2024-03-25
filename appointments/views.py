from django.utils import timezone
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from appointments.constants.enums import APPOINTMENT_STATUS_CHOICES, CANCELLED_BY_PATIENT, CANCELLED_BY_THERAPIST, COMPLETED, CONFIRMED, INACTIVE, ACTIVE, PATIENT_FIELD, PENDING_PATIENT, PENDING_THERAPIST, REFERRER_FIELD, REFERRER_OR_REFEREE_FIELD, UPDATEABLE_APPOINTMENT_STATI
from appointments.models import Appointment, AvailabilityTimeSlot, PatientReferralRequest, TherapistAssignment
from .serializers import AppointmentCreateSerializer, AppointmentReadSerializer, AppointmentUpdateSerializer, AvailabilityTimeSlotDestroySerializer, AvailabilityTimeslotSingleUpdateSerializer, HttpErrAppointmentCreateSerializer, HttpAppointmentCreateSerializer, HttpAppointmentListSerializer, HttpAppointmentRetrieveSerializer, HttpErrAppointmentUpdateSerializer, HttpErrReferralRequestCreateSerializer, HttpErrReferralRequestReplySerializer, HttpErroReferralRequestUpdateSerializer, HttpErrorAvailabilityTimeslotDestroyErrorResponse, HttpErrorAvailabilityTimeslotSingleUpdateResponse, HttpErrorSingleCreateTimeslotResponse, HttpReferralRequestCreateResponseSerializer, HttpReferralRequestReplyResponseSerializer, HttpSuccessAppointmentUpdateSerializer, HttpAvailabilityTimeslotUpdateSuccessResponse, ReferralRequestReadSerializer,  AvailabilityTimeslotBatchCreateSerializer, AvailabilityTimeslotBatchUploadSerializer, AvailabilityTimeslotCreateSerializer, AvailabilityTimeslotReadSerializer, HttpAvailabilityTimeslotCreateResponseSerializer, HttpAvailabilityTimeslotListSerializer, HttpAvailabilityTimeslotRetrieveSerializer, HttpErrorAvailabilityTimeslotBatchCreateResponse,  HttpReferralRequestListSerializer, HttpReferralRequestRetrieveSerializer, HttpSuccessReferralRequestUpdateResponseSerializer, ReferralRequestCreateSerializer, ReferralRequestReplySerializer, ReferralRequestUpdateSerializer, AvailabilityTimeslotBatchUpdateSerializer
from authentication.mixins import ActionBasedPermMixin
from authentication.utils import HasPerm
from core.enums import QuerysetBranching, UserRole
from core.http import Response, ValidationError
from core.mixins import QuerysetMapperMixin, SerializerMapperMixin
from authentication.permissions import IsPatient, IsTherapist
from core.types import DatetimeInterval, WeeklyTimeSchedule
from core.utils.time import TimeUtil
from core.viewssets import AugmentedViewSet
import rest_framework.status as status
from drf_yasg.utils import swagger_auto_schema
from core.querysets import  OwnedQS, PatientOwnedQS, QSWrapper, TherapistOwnedQS
from core.renderer import FormattedJSONRenderrer
from core.serializers import HttpErrorResponseSerializer, HttpSuccessResponseSerializer
from core.http import Response
from django.utils.translation import gettext as _
from django.db.models import Q

# TODO: use transactions for intensive operations

class AppointmentsViewset(AugmentedViewSet, ListModelMixin, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin):
    """View for appointments functionality"""


    ordering_fields = ['start_at']
    ordering = ['start_at']
    filterset_fields = {
        'status': ['iexact'],
        'start_at': ['gte', 'lte'],
        'timeslot__therapist': ['exact'],
        'timeslot': ['isnull', 'exact']
    }


    action_permissions = {
        'list': [IsAuthenticated],
        'retrieve': [IsAuthenticated],
        'create': [IsAuthenticated],
        'update': [IsAuthenticated],
        'partial_update': [IsAuthenticated],
        'cancel': [IsPatient() | IsTherapist()],
        'confirm': [IsPatient() | IsTherapist()],
        'complete': [IsTherapist()]
       
    }
    serializer_class_by_action = {
        'list': AppointmentReadSerializer,
        'retrieve': AppointmentReadSerializer,
        'create': AppointmentCreateSerializer,
        'update': AppointmentUpdateSerializer,
        'partial_update': AppointmentUpdateSerializer,
    }

    queryset_by_action = {
        'list': QSWrapper(Appointment.objects.all().prefetch_related('timeslot__therapist__user'))\
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
        'update': QSWrapper(Appointment.objects.all())\
                        .branch({
                        UserRole.PATIENT.value: PatientOwnedQS(ownership_fields=[PATIENT_FIELD]),
                        UserRole.THERAPIST.value: TherapistOwnedQS(ownership_fields=['timeslot__therapist'])
                        },
                        by=QuerysetBranching.USER_GROUP, 
                        ),
        'partial_update': QSWrapper(Appointment.objects.all())\
                        .branch({
                        UserRole.PATIENT.value: PatientOwnedQS(ownership_fields=[PATIENT_FIELD]),
                        UserRole.THERAPIST.value: TherapistOwnedQS(ownership_fields=['timeslot__therapist'])
                        },
                        by=QuerysetBranching.USER_GROUP, 
                        ),
        'cancel': QSWrapper(Appointment.objects.filter(Q(status=CONFIRMED) | Q(status=PENDING_PATIENT) | Q(status=PENDING_THERAPIST)))\
                        .branch({
                        UserRole.PATIENT.value: PatientOwnedQS(ownership_fields=['patient']),
                        UserRole.THERAPIST.value: TherapistOwnedQS(ownership_fields=['timeslot__therapist'])
                        },
                        by=QuerysetBranching.USER_GROUP, 
                        ),
        'confirm': QSWrapper(Appointment.objects.filter(Q(status=PENDING_THERAPIST) | Q(status=PENDING_PATIENT)))\
                        .branch({
                        UserRole.PATIENT.value: PatientOwnedQS(ownership_fields=['patient']),
                        UserRole.THERAPIST.value: TherapistOwnedQS(ownership_fields=['timeslot__therapist'])
                        },
                        by=QuerysetBranching.USER_GROUP, 
                        ),
        'complete': QSWrapper(Appointment.objects.filter(status=CONFIRMED)
                        .select_related('timeslot__therapist'))\
                        .branch({
                        UserRole.THERAPIST.value: TherapistOwnedQS(ownership_fields=['timeslot__therapist'])
                        },
                        by=QuerysetBranching.USER_GROUP, 
                        ),
        
    }

    @swagger_auto_schema(responses={status.HTTP_200_OK: HttpAppointmentListSerializer()})
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(responses={status.HTTP_200_OK: HttpAppointmentRetrieveSerializer()})
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

   
    @swagger_auto_schema(responses={status.HTTP_200_OK: HttpAppointmentCreateSerializer(), status.HTTP_400_BAD_REQUEST: HttpErrAppointmentCreateSerializer()})
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(responses={status.HTTP_200_OK: HttpSuccessAppointmentUpdateSerializer(), status.HTTP_400_BAD_REQUEST: HttpErrAppointmentUpdateSerializer()})
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(responses={status.HTTP_200_OK: HttpSuccessAppointmentUpdateSerializer(), status.HTTP_400_BAD_REQUEST: HttpErrAppointmentUpdateSerializer()})
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)
    
    @swagger_auto_schema(responses={200: HttpSuccessResponseSerializer(), 400: HttpErrorResponseSerializer()})
    @action(methods=['PATCH'], detail=True)
    def confirm(self, request, *args, **kwargs):
        """
            Confirm a pending appointment
        """
        instance: Appointment = self.get_object()

        if hasattr(request.user, 'therapist_profile') and instance.status != PENDING_THERAPIST:
            raise ValidationError(_('a patient confirm an appointment that is not pending therapist confirmation'))

        if hasattr(request.user, 'patient_profile') and instance.status != PENDING_PATIENT:
            raise ValidationError(_('a therapist confirm an appointment that is not pending patient confirmation'))

        instance.status = CONFIRMED
        instance.save()
        return Response(data=None, status=status.HTTP_200_OK, message=_('Appointment confirmed successfully'))

    @swagger_auto_schema(responses={200: HttpSuccessResponseSerializer()})    
    @action(methods=['PATCH'], detail=True)
    def cancel(self, request, *args, **kwargs):
        """
            Cancel an appointment
        """

        instance: Appointment = self.get_object()
        if hasattr(request.user, 'therapist_profile'):
            instance.status = CANCELLED_BY_THERAPIST
        elif hasattr(request.user, 'patient_profile'):
            instance.status = CANCELLED_BY_PATIENT
        else:
            raise ValidationError(_('Only patients and therapists can cancel appointments'))
        
        TherapistAssignment.objects.filter(therapist_timeslot=instance.timeslot, status=ACTIVE).update(status=INACTIVE)
        instance.save()

        return Response(data=None, status=status.HTTP_200_OK, message=_('Appointment cancelled successfully'))

    @swagger_auto_schema(responses={200: HttpSuccessResponseSerializer(), 400: HttpErrorResponseSerializer()})
    @action(methods=['PATCH'], detail=True)
    def complete(self, request, *args, **kwargs):

        instance = self.get_object()

        if instance.start_at > timezone.now():
            raise ValidationError(_('You can only complete appointments that have already started'))
        
        instance.status = COMPLETED
        instance.save()
    
        return Response(data=None, status=status.HTTP_200_OK, message=_('Appointment completed successfully'))


class AvailabilityTimeslotViewset(AugmentedViewSet, ListModelMixin, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin, DestroyModelMixin):
    """View for availability timeslot functionality"""

    ordering_fields = ['start_at']
    ordering = ['start_at']
    filterset_fields = {
        'start_at': ['gte', 'lte'],
        'end_at': ['gte', 'lte'],
        'therapist': ['exact'],
        'active': ['exact']
    }
    
    action_permissions = {
        'list': [IsAuthenticated],
        'retrieve': [IsAuthenticated],
        'create': [IsTherapist()],
        'batch_create': [IsTherapist()],
        'update': [IsTherapist()],
        'partial_update': [IsTherapist()],
        'batch_update': [IsTherapist()],
        'destroy': [IsTherapist()]       
    }

    serializer_class_by_action = {
        'list': AvailabilityTimeslotReadSerializer ,
        'retrieve': AvailabilityTimeslotReadSerializer,
        'create': AvailabilityTimeslotCreateSerializer,
        'batch_create': AvailabilityTimeslotBatchCreateSerializer,
        'update': AvailabilityTimeslotSingleUpdateSerializer,
        'partial_update': AvailabilityTimeslotSingleUpdateSerializer,
        'batch_update': AvailabilityTimeslotBatchUpdateSerializer,
        'destroy': AvailabilityTimeSlotDestroySerializer
    }

    queryset_by_action = {
        'list': AvailabilityTimeSlot.objects.filter(active=True).select_related('therapist__user'),
        'retrieve': AvailabilityTimeSlot.objects.filter(active=True).prefetch_related('therapist__user', 'linked_appointments__patient__user'),
        'update': QSWrapper(AvailabilityTimeSlot.objects.filter(active=True))
                    .branch({
                        UserRole.THERAPIST.value: TherapistOwnedQS()
                        },
                        by=QuerysetBranching.USER_GROUP, 
                        ),
        'partial_update': QSWrapper(AvailabilityTimeSlot.objects.filter(active=True))
                    .branch({
                        UserRole.THERAPIST.value: TherapistOwnedQS()
                        },
                        by=QuerysetBranching.USER_GROUP, 
                        ),
        'batch_update': QSWrapper(AvailabilityTimeSlot.objects.filter(active=True))
                        .branch({
                            UserRole.THERAPIST.value: TherapistOwnedQS()
                            },
                            by=QuerysetBranching.USER_GROUP),
        'destroy': QSWrapper(AvailabilityTimeSlot.objects.filter(active=True))
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

   
    @swagger_auto_schema(responses={200: HttpAvailabilityTimeslotCreateResponseSerializer(), status.HTTP_400_BAD_REQUEST: HttpErrorSingleCreateTimeslotResponse()})
    def create(self, request, *args, **kwargs):
        """
            Creates one or more availability timeslots with no recurrence

             **@validation**:
                - all passed time intervals must not conflict with each other
                - the schedule created from the specified intervals must not conflict with any existing timeslots
        """
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(responses={200: None, status.HTTP_400_BAD_REQUEST: HttpErrorAvailabilityTimeslotBatchCreateResponse()})
    @action(methods=['POST'], detail=False)
    def batch_create(self, request, *args, **kwargs):
        """
            Creating a group of timeslots by specifiyng a weekly schedule with multiple time intervals along a date span

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
    
    @swagger_auto_schema(responses={200: HttpAvailabilityTimeslotUpdateSuccessResponse(), 400: HttpErrorAvailabilityTimeslotSingleUpdateResponse()})
    @action(
        methods=['PUT'],
        detail=True,
    )
    def batch_update(self, request, *args, **kwargs):

        instance = self.get_object()
        serializer = self.get_serializer(instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    # TODO: add error serializers
    @swagger_auto_schema(responses={200: HttpAvailabilityTimeslotUpdateSuccessResponse(), 400:HttpErrorAvailabilityTimeslotSingleUpdateResponse()})
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(responses={200: HttpAvailabilityTimeslotUpdateSuccessResponse(), 400: HttpErrorAvailabilityTimeslotSingleUpdateResponse()})
    def partial_update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(responses={200: None,400: HttpErrorAvailabilityTimeslotDestroyErrorResponse()})
    def destroy(self, request, *args, **kwargs):

        instance = self.get_object()
        
        serializer = self.get_serializer(instance=instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        # when using force_drop flag, drop all linked appointments in the future
        
        if serializer.data.get('force_drop', False):
            dropped_appointments = instance.linked_appointments.filter(
                start_at__gt=timezone.now()
            )

            

            affected_ids = [appointment.id for appointment in dropped_appointments]

            dropped_appointments.update(status=PENDING_THERAPIST, timeslot=None)

            TherapistAssignment.objects.filter(appointment__pk__in=affected_ids).update(status=INACTIVE)
        
        instance.active = False
        instance.save()

        return Response(data=None, message=_("Time slot deleted successfully"), status=status.HTTP_200_OK)
    



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
        'update': [IsPatient()], ## discusee if we should include educator roles outside normal user boundaries
        'partial_update': [IsPatient()],
        'reply': [IsTherapist()],
        
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
                        UserRole.PATIENT.value: OwnedQS(ownership_fields= [REFERRER_FIELD])
                        },
                        by=QuerysetBranching.USER_GROUP, 
                        pass_through=[UserRole.THERAPIST.value]),
        'retrieve': QSWrapper(PatientReferralRequest.objects.all().select_related('responding_therapist__user'))
                    .branch({
                        UserRole.PATIENT.value: OwnedQS(ownership_fields=[REFERRER_FIELD])
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

    @swagger_auto_schema(responses={200: HttpReferralRequestCreateResponseSerializer(), status.HTTP_400_BAD_REQUEST: HttpErrReferralRequestCreateSerializer()})
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(responses={200: HttpSuccessReferralRequestUpdateResponseSerializer(), status.HTTP_400_BAD_REQUEST: HttpErroReferralRequestUpdateSerializer()})
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(responses={200: HttpSuccessReferralRequestUpdateResponseSerializer(partial=True), status.HTTP_400_BAD_REQUEST: HttpErroReferralRequestUpdateSerializer()})
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(responses={200: HttpReferralRequestReplyResponseSerializer(), status.HTTP_400_BAD_REQUEST: HttpErrReferralRequestReplySerializer()})    
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

