
from rest_framework.routers import DefaultRouter
from .views import KFUPMDeptViewset

router = DefaultRouter()

router.register(r'kfupm-departments', KFUPMDeptViewset, basename='kfupm-departments')

urlpatterns = router.urls