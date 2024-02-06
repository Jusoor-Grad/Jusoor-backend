from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from appointments.models import Appointment
from appointments.serializers.appointments import AppointmentCreateSerializer, AppointmentReadSerializer, AppointmentUpdateSerializer
from authentication.mixins import ActionBasedPermMixin
from authentication.utils import HasPerm
from core.http import Response
from core.mixins import QuerysetMapperMixin, SerializerMapperMixin
from authentication.permissions import IsPatient, IsTherapist
import rest_framework.status as status
from drf_yasg.utils import swagger_auto_schema

from core.renderer import FormattedJSONRenderrer

class AppointmentsViewset(ActionBasedPermMixin, SerializerMapperMixin, QuerysetMapperMixin, GenericViewSet, ListModelMixin, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin):
    """View for appointments functionality"""

    renderer_classes = [FormattedJSONRenderrer]

    action_permissions = {
        'list': [IsAuthenticated],
        'retrieve': [IsAuthenticated],
        'create': [IsPatient],
        'update': [IsTherapist],
       
    }
    serializer_class_by_action = {
        'list': AppointmentReadSerializer,
        'retrieve': AppointmentReadSerializer,
        'create': AppointmentCreateSerializer,
        'update': AppointmentUpdateSerializer,
    }


    queryset_by_action = {
        'list': Appointment.objects.all().select_related('timeslot__therapist__user'),
        'retrieve': Appointment.objects.all().select_related('timeslot__therapist__user'),
        'create': None,
        'update': None,
    }

   
    
    # def list(self, request):
    #     """list all appointments for the logged in user"""
    #     pass

   
    
    # def retrieve(self, request):
    #     """retrieve a specific appointment for the logged in user"""
    #     pass

   
    
    def create(self, request):
        """create a new appointment for the logged in user"""
        pass

   
    
    def update(self, request):
        """update a specific appointment for the logged in user"""
        pass


class AvailabilityTimeslotViewset(ActionBasedPermMixin, SerializerMapperMixin, GenericViewSet, ListModelMixin, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin):
    """View for availability timeslot functionality"""

    action_permissions = {
        'list': [HasPerm('list')],
        'retrieve': [HasPerm('retrieve')],
        'create': [HasPerm('create')],
        'update': [HasPerm('update')],
       
    }
    serializer_class_by_action = {
        'list': None,
        'retrieve': None,
        'create': None,
        'update': None,
    }

   
    
    def list(self, request):
        """list all availability timeslots for the logged in user"""
        pass

   
    
    def retrieve(self, request):
        """retrieve a specific availability timeslot for the logged in user"""
        pass

   
    
    def create(self, request):
        """create a new availability timeslot for the logged in user"""
        pass

   
    
    def update(self, request):
        """update a specific availability timeslot for the logged in user"""
        pass


class ReferralViewset(ActionBasedPermMixin, SerializerMapperMixin, GenericViewSet, ListModelMixin, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin):
    """View for referral functionality"""

    action_permissions = {
        'list': [HasPerm('list')],
        'retrieve': [HasPerm('retrieve')],
        'create': [HasPerm('create')],
        'update': [HasPerm('update')],
       
    }
    serializer_class_by_action = {
        'list': None,
        'retrieve': None,
        'create': None,
        'update': None,
    }

   
    
    def list(self, request):
        """list all referrals for the logged in user"""
        pass

   
    
    def retrieve(self, request):
        """retrieve a specific referral for the logged in user"""
        pass

   
    
    def create(self, request):
        """create a new referral for the logged in user"""
        pass

   
    
    def update(self, request):
        """update a specific referral for the logged in user"""
        pass