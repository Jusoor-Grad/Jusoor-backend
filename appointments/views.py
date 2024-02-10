from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from appointments.constants.enums import APPOINTMENT_STATUS_CHOICES, CANCELLED, REFERRER_FIELD, REFERRER_OR_REFEREE_FIELD, UPDATEABLE_APPOINTMENT_STATI
from appointments.models import Appointment, AvailabilityTimeSlot, PatientReferralRequest
from appointments.serializers.appointments import AppointmentCreateSerializer, AppointmentReadSerializer, AppointmentUpdateSerializer, HttpAppointmentCreateSerializer, HttpAppointmentListSerializer, HttpAppointmentRetrieveSerializer
from appointments.serializers.referrals import ReferralRequestReadSerializer
from appointments.serializers.timeslots import AvailabilityTimeslotCreateSerializer, AvailabilityTimeslotReadSerializer, HttpAvailabilityTimeslotListSerializer, HttpAvailabilityTimeslotRetrieveSerializer
from authentication.mixins import ActionBasedPermMixin
from authentication.utils import HasPerm
from core.enums import QuerysetBranching, UserRole
from core.http import Response
from core.mixins import QuerysetMapperMixin, SerializerMapperMixin
from authentication.permissions import IsPatient, IsTherapist
from .serializers.referrals import HttpReferralRequestListSerializer, HttpReferralRequestRetrieveSerializer, HttpReferralRequestUpdateResponseSerializer, ReferralRequestCreateSerializer, ReferralRequestReplySerializer, ReferralRequestUpdateSerializer
import rest_framework.status as status
from drf_yasg.utils import swagger_auto_schema
from core.querysets import  OwnedQS, PatientOwnedQS, QSWrapper, TherapistOwnedQS
from core.renderer import FormattedJSONRenderrer
from core.serializers import HttpErrorResponseSerializer, HttpSuccessResponeSerializer
from core.http import Response
from django.utils.translation import gettext as _

class AppointmentsViewset(ActionBasedPermMixin, SerializerMapperMixin, QuerysetMapperMixin, GenericViewSet, ListModelMixin, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin):
    """View for appointments functionality"""

    renderer_classes = [FormattedJSONRenderrer]

    def get_queryset(self):
        return super().get_queryset()

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
                        UserRole.PATIENT.value: PatientOwnedQS(ownership_fields=['patient'])
                        },
                        by=QuerysetBranching.USER_GROUP, 
                        pass_through=[UserRole.THERAPIST.value]),
        'retrieve': QSWrapper(Appointment.objects.all())\
                        .branch({
                        UserRole.PATIENT.value: PatientOwnedQS(ownership_fields=['patient'])
                        },
                        by=QuerysetBranching.USER_GROUP, 
                        pass_through=[UserRole.THERAPIST.value]),
        'create': QSWrapper(Appointment.objects.all())\
                        .branch({
                        UserRole.PATIENT.value: PatientOwnedQS(ownership_fields=['patient'])
                        },
                        by=QuerysetBranching.USER_GROUP, 
                        pass_through=[UserRole.THERAPIST.value]),
        # TODO: test the endpoint formally
        'update': QSWrapper(Appointment.objects.all())\
                        .branch({
                        UserRole.PATIENT.value: PatientOwnedQS(ownership_fields=['patient']),
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

#    TODO: query params for temporal filtering
    @swagger_auto_schema(responses={status.HTTP_200_OK: HttpAppointmentListSerializer()})
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(responses={status.HTTP_200_OK: HttpAppointmentRetrieveSerializer()})
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

   
    @swagger_auto_schema(responses={status.HTTP_200_OK: HttpAppointmentCreateSerializer(), status.HTTP_400_BAD_REQUEST: HttpErrorResponseSerializer()})
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(responses={status.HTTP_200_OK: HttpAppointmentCreateSerializer(), status.HTTP_400_BAD_REQUEST: HttpErrorResponseSerializer()})
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



class AvailabilityTimeslotViewset(ActionBasedPermMixin, SerializerMapperMixin, QuerysetMapperMixin, GenericViewSet, ListModelMixin, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin):
    """View for availability timeslot functionality"""

    renderer_classes = [FormattedJSONRenderrer]

    action_permissions = {
        'list': [IsAuthenticated],
        'retrieve': [IsAuthenticated],
        'create': [IsTherapist()],
        'update': [IsTherapist()],
       
    }
    serializer_class_by_action = {
        'list': AvailabilityTimeslotReadSerializer ,
        'retrieve': AvailabilityTimeslotReadSerializer,
        'create': AvailabilityTimeslotCreateSerializer,
        'update': None,
    }

    queryset_by_action = {
        'list': AvailabilityTimeSlot.objects.all().select_related('therapist__user'),
        'retrieve': AvailabilityTimeSlot.objects.all().select_related('therapist__user'),
        'update': QSWrapper(AvailabilityTimeSlot.objects.all())
                    .branch({
                        UserRole.PATIENT.value: OwnedQS(ownership_fields=[UserRole.PATIENT.value])
                        },
                        by=QuerysetBranching.USER_GROUP, 
                        pass_through=[UserRole.THERAPIST.value])
    }
   
    
    @swagger_auto_schema(responses={200: HttpAvailabilityTimeslotListSerializer()})
    def list(self, request, *args, **kwargs):
        return (super().list(request, *args, **kwargs))

   
    
    @swagger_auto_schema(responses={200: HttpAvailabilityTimeslotRetrieveSerializer()})
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

   
    # TODO: create custom batch creation of timeslots
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

   
    
    def update(self, request):
        """update a specific availability timeslot for the logged in user"""
        pass


class ReferralViewset(ActionBasedPermMixin, SerializerMapperMixin, QuerysetMapperMixin, GenericViewSet, ListModelMixin, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin):
    """View for referral functionality"""

    renderer_classes = [FormattedJSONRenderrer]
    
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

        return self.perform_update(serializer)

