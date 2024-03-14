from rest_framework.routers import SimpleRouter
from .views import ChatMessageViewset, ChatRoomFeedbackResponseViewset, ChatRoomFeedbackViewset, ChatBotViewset

router = SimpleRouter()

router.register(r'messages', ChatMessageViewset, basename='chat-messages')
# router.register(r'rooms', ChatRoomViewset, basename='chat-rooms')
router.register(r'chatbots', ChatBotViewset, basename='chat-bots')
router.register(prefix=r'reports', viewset=ChatRoomFeedbackViewset, basename='reports')
router.register('report-responses', ChatRoomFeedbackResponseViewset, basename='report-responses')

urlpatterns = router.urls
