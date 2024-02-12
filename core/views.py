from core.models import KFUPMDepartment
from core.serializers import HttpKFUPMDepartmentDetailResponseSerializer, KFUPMDepartmentSerializer
from core.viewssets import AugmentedViewSet
from rest_framework.permissions import AllowAny
from rest_framework.mixins import ListModelMixin
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status

class KFUPMDeptViewset(AugmentedViewSet, ListModelMixin):
    """Viewset for KFUPMDept"""

    queryset = KFUPMDepartment.objects.all()
    serializer_class = KFUPMDepartmentSerializer
    permission_classes = [AllowAny]
    
    search_fields = ['short_name', 'long_name']
    ordering_fields = ['short_name', 'long_name']
    ordering =  ['short_name']
    filterset_fields = ['short_name', 'long_name']

    @swagger_auto_schema(responses={status.HTTP_200_OK: HttpKFUPMDepartmentDetailResponseSerializer()})
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)