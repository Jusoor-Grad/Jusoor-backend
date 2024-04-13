from authentication.models import User
from authentication.permissions import IsPatient, IsTherapist
from authentication.serializers import PaginatedPatientResponseSerializer, HttpPatientReadResponseSerializer, HttpTherapistListResponseSerializer, HttpTherapistReadResponseSerializer, PatientHttpListResposneSerializer, PatientReadSerializer, PatientRetrieveSerializer
from core.enums import QuerysetBranching, UserRole
from core.models import KFUPMDepartment
from core.querysets import PatientOwnedQS, QSWrapper
from core.serializers import HttpCounterSerializer, HttpErrorResponseSerializer, HttpKFUPMDepartmentListResponseSerializer, HttpKFUPMDepartmentRetrieveResponseSerializer,  KFUPMDepartmentSerializer
from core.viewssets import AugmentedViewSet
from rest_framework.permissions import AllowAny
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from django.utils.translation import gettext as _
from rest_framework.decorators import action
from django.utils import timezone
from datetime import timedelta
from dateutil.relativedelta import relativedelta
class KFUPMDeptViewset(AugmentedViewSet, ListModelMixin):
    """Viewset for KFUPMDept"""

    queryset = KFUPMDepartment.objects.all()
    serializer_class = KFUPMDepartmentSerializer
    permission_classes = [AllowAny]
    
    search_fields = ['short_name', 'long_name']
    ordering_fields = ['short_name', 'long_name']
    ordering =  ['short_name']
    filterset_fields = ['short_name', 'long_name']

    @swagger_auto_schema(responses={status.HTTP_200_OK: HttpKFUPMDepartmentListResponseSerializer()})
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


# TODO: add the patient sentiument profile in the future
class PatientViewSet(AugmentedViewSet, ListModelMixin, RetrieveModelMixin):

    serializer_class = PatientReadSerializer

    serializer_class_by_action = {
        'list': PatientReadSerializer,
        'retrieve': PatientRetrieveSerializer
    }

    action_permissions = {
        'list': [IsTherapist()],
        "retrieve": [IsTherapist()],
        'count': [IsTherapist()],
        'active_count': [IsTherapist()]
    }

    filterset_fields = ['patient_profile__department__short_name', 'patient_profile__department__long_name', 'username', 'email']
    queryset= User.objects.filter(patient_profile__isnull=False).select_related('patient_profile__department')
     

    @swagger_auto_schema(responses={status.HTTP_200_OK: PatientHttpListResposneSerializer()})
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    

    @swagger_auto_schema(responses={status.HTTP_200_OK: HttpPatientReadResponseSerializer(), status.HTTP_403_FORBIDDEN: HttpErrorResponseSerializer(), status.HTTP_404_NOT_FOUND: HttpErrorResponseSerializer()})
    def retrieve(self, request, *args, **kwargs):
        """
            Fetch a single user profile by either the owner patien or any active therapist
        """

        if request.user.groups.filter(name=UserRole.THERAPIST.value).exists():
            return super().retrieve(request, *args, **kwargs)
        elif request.user.groups.filter(name=UserRole.PATIENT.value).exists():
            self.queryset = self.queryset.filter(id=request.user.id)
            return super().retrieve(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN, data= {"message": _("You do not have permission to perform this action")})

    @swagger_auto_schema(responses={status.HTTP_200_OK: HttpCounterSerializer()})
    @action(detail=False, methods=['get'])
    def count(self, request, *args, **kwargs):
        """
            Get the count of patients
        """
        
        current_count = self.filter_queryset(self.get_queryset()).count()
        last_month_end_timestamp = timezone.now().replace(day=1, hour=23, minute=59, second=59) - timedelta(days=1)
        last_month_count = self.filter_queryset(self.get_queryset().filter(created_at__lte=last_month_end_timestamp)).count()

        return Response(data={"current_count": current_count, "last_month_count": last_month_count})
    
    @swagger_auto_schema(responses={status.HTTP_200_OK: HttpCounterSerializer()})
    @action(detail=False, methods=['get'])
    def active_count(self, request, *args, **kwargs):
        """
            Get the count of active patients
        """

        current_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_start = current_month_start - relativedelta(months=1)
        
        current_count = self.filter_queryset(self.get_queryset().filter(last_activity__gte=current_month_start)).count()
        last_month_count = self.filter_queryset(self.get_queryset().filter(last_activity__gte=last_month_start, last_activity__lt=current_month_start)).count()

        return Response(data={"current_count": current_count, "last_month_count": last_month_count})
    
class TherapistViewSet(AugmentedViewSet, ListModelMixin, RetrieveModelMixin):

    serializer_class = PatientReadSerializer

    action_permissions = {
        'list': [IsTherapist() | IsPatient()],
        "retrieve": [IsTherapist() | IsPatient()]
    }

    queryset= User.objects.filter(therapist_profile__isnull=False).select_related('therapist_profile__department')
     

    @swagger_auto_schema(responses={status.HTTP_200_OK: HttpTherapistListResponseSerializer()})
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    

    @swagger_auto_schema(responses={status.HTTP_200_OK: HttpTherapistReadResponseSerializer(), status.HTTP_404_NOT_FOUND: HttpErrorResponseSerializer()})
    def retrieve(self, request, *args, **kwargs):
        """
            Fetch a single user profile by either the owner patien or any active therapist
        """
        return super().retrieve(request, *args, **kwargs)

