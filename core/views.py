from authentication.models import User
from authentication.permissions import IsPatient, IsTherapist
from authentication.serializers import PaginatedPatientResponseSerializer, HttpPatientReadResponseSerializer, HttpTherapistListResponseSerializer, HttpTherapistReadResponseSerializer, PatientHttpListResposneSerializer, PatientReadSerializer
from core.enums import QuerysetBranching, UserRole
from core.models import KFUPMDepartment
from core.querysets import PatientOwnedQS, QSWrapper
from core.serializers import HttpErrorResponseSerializer, HttpKFUPMDepartmentListResponseSerializer, HttpKFUPMDepartmentRetrieveResponseSerializer,  KFUPMDepartmentSerializer
from core.viewssets import AugmentedViewSet
from rest_framework.permissions import AllowAny
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from django.utils.translation import gettext as _
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

    action_permissions = {
        'list': [IsTherapist()],
        "retrieve": [IsTherapist() | IsPatient()]
    }

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
            print('HERE!')
            return super().retrieve(request, *args, **kwargs)
        elif request.user.groups.filter(name=UserRole.PATIENT.value).exists():
            self.queryset = self.queryset.filter(id=request.user.id)
            return super().retrieve(request, *args, **kwargs)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN, data= {"message": _("You do not have permission to perform this action")})

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

