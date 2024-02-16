
from rest_framework.routers import DefaultRouter
from .views import KFUPMDeptViewset, PatientViewSet

router = DefaultRouter()

router.register(r'kfupm-departments', KFUPMDeptViewset, basename='kfupm-departments')
router.register(r'patients', PatientViewSet, basename='patients')

urlpatterns = router.urls