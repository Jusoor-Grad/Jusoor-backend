
from rest_framework.routers import DefaultRouter
from .views import KFUPMDeptViewset, PatientViewSet, TherapistViewSet

router = DefaultRouter()

router.register(r'kfupm-departments', KFUPMDeptViewset, basename='kfupm-departments')
router.register(r'patients', PatientViewSet, basename='patients')
router.register(r'therapists', TherapistViewSet, basename='therapists')

urlpatterns = router.urls