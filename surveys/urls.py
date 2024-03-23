from django.db import router
from rest_framework.routers import SimpleRouter

from surveys.views import TherapistSurveyViewset, TherapistSurveyQuestionViewset, TherapistSurveyResponseViewset

router = SimpleRouter()

router.register(r'', TherapistSurveyViewset, basename='surveys')
router.register(r'survey-questions', TherapistSurveyQuestionViewset, basename='survey-questions')
router.register(r'survey-responses', TherapistSurveyResponseViewset, basename='survey-responses')

urlpatterns = router.urls