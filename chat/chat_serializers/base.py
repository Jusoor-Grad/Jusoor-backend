
from rest_framework import serializers
from authentication.serializers import UserReadSerializer
import chat
from chat.models import ChatBot, ChatMessage,  ChatRoomFeedbackResponse, ChatRoomFeedeback
from core.http import ValidationError
from django.utils.translation import gettext_lazy as _
from chat.enums import PENDING, REVIEWED
# ------------------------------ chat messages ------------------------------

class ChatMessageReadSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatMessage
        fields = '__all__'

class ChatMessageCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatMessage
        fields = ['content']

    
# --------------------------- chat bots ------------------------------
    
class ChatBotFullReadSerializer(serializers.ModelSerializer):
    
        user_profile = UserReadSerializer()
    
        class Meta:
            model = ChatBot
            fields = '__all__'

class ChatBotReadSerializer(serializers.ModelSerializer):
     
        class Meta:
            model = ChatBot
            fields = ['name', 'id']

class ChatBotWriteSerializer(serializers.ModelSerializer):
     
     class Meta:
            model = ChatBot
            fields = '__all__'

# ------------------------------ chat rooms ------------------------------    

# class ChatRoomReadSerializer(serializers.ModelSerializer):

#     unread_messages = serializers.SerializerMethodField()
#     user = UserReadSerializer()
#     bot = ChatBotReadSerializer()

#     def get_unread_messages(self, obj):
#         return obj.messages.filter(read=False).count()

#     class Meta:
#         model = chat.models.ChatRoom
#         fields = ['bot', 'user', 'unread_messages', 'last_updated_at', "id"]


# class ChatRoomCreateSerializer(serializers.ModelSerializer):
    
#         class Meta:
#             model = chat.models.ChatRoom
#             fields = ['bot']
    
#         def validate(self, attrs):
    
#             # making sure the user and the bot do not already have a chat room together
#             bot = attrs.get('bot')
            
#             if chat.models.ChatRoom.objects.filter(bot=bot, user=self.context['request'].user).exists():
#                 raise ValidationError(_('You already have a chat room with this bot'))
            
#             return attrs
        
#         def create(self, validated_data):
    
#             chat_room, _ = chat.models.ChatRoom.objects.get_or_create(
#                 user=self.context['request'].user,
#                 **validated_data
#             )
    
#             return chat_room
        
        
# ------------------------------ feedback ------------------------------
class ReportChatroomCreateSerializer(serializers.Serializer):
    """
        Serializer used to report a chat room
    """
    feedback = serializers.CharField()
    target_message = serializers.PrimaryKeyRelatedField(queryset=ChatMessage.objects.all())

    def validate(self, attrs):

        message = attrs.get('target_message')

        # make sure the user is a part of the specified chat room
        if not chat.sender == self.context['request'].user and not chat.receiver == self.context['request'].user:
            raise ValidationError(_('You are not allowed to report this message'))

        
        return attrs
    
    def create(self, validated_data):

        report = ChatRoomFeedeback.objects.create(
            patient=self.context['request'].user.patient_profile,
            **validated_data,
            status= PENDING
        )

        return report
    
class ChatRoomReportReadSerializer(serializers.ModelSerializer):
    
        class Meta:
            model = ChatRoomFeedeback
            fields = '__all__'
            depth =2

class ChatRoomReportResponseReadSerializer(serializers.ModelSerializer):

        therapist = UserReadSerializer()
        feedback = ChatRoomReportReadSerializer()

        class Meta:
            model = ChatRoomFeedbackResponse
            fields = '__all__'
            

class ReviewChatRoomFeedbackSerializer(serializers.Serializer):
    """
        Serializer used to review a chat room feedback
    """
    feedback = serializers.PrimaryKeyRelatedField(queryset=ChatRoomFeedeback.objects.all())
    response = serializers.CharField()

    
    def create(self, validated_data):

        response = ChatRoomFeedbackResponse.objects.create(
            therapist=self.context['request'].user.therapist_profile,
            **validated_data
        )

        validated_data['feedback'].status = REVIEWED
        validated_data['feedback'].save()

        return response
    

