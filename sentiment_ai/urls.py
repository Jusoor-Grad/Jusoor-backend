from rest_framework.routers import DefaultRouter

from sentiment_ai.views import MessageSentimentViewset, SentimentReportViewset

router = DefaultRouter()

router.register('sentiment-reports', SentimentReportViewset, basename='sentiment-reports')
router.register('message-sentiments', MessageSentimentViewset, basename='message-sentiments')

urlpatterns = router.urls

