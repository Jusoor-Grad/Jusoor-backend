from chat.chat_serializers.base import ChatBotFullReadSerializer, ChatBotReadSerializer, ChatBotWriteSerializer, ChatMessageReadSerializer,  ChatRoomReportReadSerializer, ChatRoomReportResponseReadSerializer, ReviewChatRoomFeedbackSerializer
from core.serializers import HttpErrorResponseSerializer, HttpErrorSerializer, HttpSuccessResponseSerializer, HttpPaginatedSerializer
from rest_framework import serializers

# ------------ chat messages

class HttpSuccessChatMessageReadSerializer(HttpSuccessResponseSerializer):
    data = ChatMessageReadSerializer()

class HttpSuccessChatMessageListSerializer(HttpPaginatedSerializer):
    results = ChatMessageReadSerializer(many=True)

class ListChatMessageHttpSuccessSerializer(HttpSuccessResponseSerializer):
    data = HttpSuccessChatMessageListSerializer()

class ChatMessageCreateErrorSerializer(serializers.Serializer):
    chat = serializers.ListSerializer(child=serializers.CharField())
    error = serializers.ListSerializer(child=serializers.CharField())
    content = serializers.ListSerializer(child=serializers.CharField())

class HttpErrorCreateChatMessageSerializer(HttpErrorResponseSerializer):
    data = ChatMessageCreateErrorSerializer()

# ------------ chat rooms



# class ChatRoomListHttpSuccessSerializer(HttpPaginatedSerializer):
#     results = ChatRoomReadSerializer(many=True)

# class ChatRoomListHttpResponseSuccessSerializer(HttpSuccessResponseSerializer):
#     data = ChatRoomListHttpSuccessSerializer()

# class ChatRoomRetrieveHttpSuccessSerializer(HttpSuccessResponseSerializer):
#     data = ChatRoomReadSerializer()


class ChatRoomInnerErrorSerializer(serializers.Serializer):
    bot = serializers.ListSerializer(child=serializers.CharField())
    error = serializers.ListSerializer(child=serializers.CharField())

class ChatRoomCreateHttpErrorSerializer(HttpErrorSerializer):
    data = ChatRoomInnerErrorSerializer()

# ------------ chat room feedback
    
class ChatRoomReportErrorSerializer(serializers.Serializer):
    chat_room = serializers.ListSerializer(child=serializers.CharField())
    error = serializers.ListSerializer(child=serializers.CharField())
    status = serializers.ListSerializer(child=serializers.CharField())
    feedback = serializers.ListSerializer(child=serializers.CharField())
    target_message = serializers.ListSerializer(child=serializers.CharField())

class HttpErrorReportChatRoomFeedbackSerializer(HttpErrorResponseSerializer):
    data = ChatRoomReportErrorSerializer()

class CreateChatRoomReportHttpSuccessSerializer(HttpPaginatedSerializer):
    results = ReviewChatRoomFeedbackSerializer()

class RetrieveChatRoomReportHttpSerializer(HttpSuccessResponseSerializer):
    data = ChatRoomReportReadSerializer()

class ListReportChatroomReportHttpSerializer(HttpPaginatedSerializer):
    results = ChatRoomReportReadSerializer(many=True)

class ListReportChatroomReportHttpSuccessResposneSerializer(HttpSuccessResponseSerializer):
    data = ListReportChatroomReportHttpSerializer()

class ReviewChatRoomFeedbackHttpSuccessSerializer(HttpSuccessResponseSerializer):
    data = ReviewChatRoomFeedbackSerializer()

class ReviewChatRoomFeedbackHttpErrorSerializer(HttpErrorResponseSerializer):
    data = ReviewChatRoomFeedbackSerializer()


class RetrieveChatRoomFeedbackResponseHttpSuccessSerializer(HttpSuccessResponseSerializer):
    data = ChatRoomReportResponseReadSerializer()

class ListChatRoomFeedbackResponseHttpSuccessSerializer(HttpPaginatedSerializer):
    results = ChatRoomReportResponseReadSerializer(many=True)

class ListChatRoomFeedbackResponseHttpSuccessResponseSerializer(HttpSuccessResponseSerializer):
    data = ListChatRoomFeedbackResponseHttpSuccessSerializer()

# ------------ chat bots
    
class ChatBotListHttpSuccessSerializer(HttpPaginatedSerializer):
    results = ChatBotReadSerializer(many=True)

class ChatBotListHttpSuccessResponseSerializer(HttpSuccessResponseSerializer):
    data = ChatBotListHttpSuccessSerializer()

class ChatBotRetrieveHttpSuccessSerializer(HttpSuccessResponseSerializer):
    data = ChatBotReadSerializer()

class ChatBotFullRetrieveHttpSuccessSerializer(HttpSuccessResponseSerializer):
    data = ChatBotFullReadSerializer()

class ChatBotWriteSerializerSuccessSerializer(HttpSuccessResponseSerializer):
    data = ChatBotReadSerializer()

class ChatBotWriteSerializerErrorSerializer(HttpErrorSerializer):
    data = ChatBotWriteSerializer()
