from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import AppointmentsViewset, AvailabilityTimeslotViewset, ReferralViewset

router = DefaultRouter()

router.register(r'appointments', AppointmentsViewset, basename='appointments')
router.register(r'timeslots', AvailabilityTimeslotViewset, basename='availability-timeslots')
router.register(r'referrals', ReferralViewset, basename='referrals')


urlpatterns = router.urls