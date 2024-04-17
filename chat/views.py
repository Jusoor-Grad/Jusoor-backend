from rest_framework.decorators import action
from yaml import serialize
from authentication.permissions import IsPatient, IsTherapist
from chat.agents import ChatGPTAgent, DummyAIAgent
from chat.chat_serializers.base import ChatBotFullReadSerializer, ChatBotReadSerializer, ChatBotWriteSerializer, ChatMessageCreateSerializer, ChatMessageReadSerializer, ChatRoomReportReadSerializer, ReportChatroomCreateSerializer, ReviewChatRoomFeedbackSerializer
from chat.chat_serializers.http import ChatBotFullRetrieveHttpSuccessSerializer, ChatBotListHttpSuccessResponseSerializer, ChatBotRetrieveHttpSuccessSerializer, ChatBotWriteSerializerSuccessSerializer, CreateChatRoomReportHttpSuccessSerializer,  HttpErrorCreateChatMessageSerializer, HttpErrorReportChatRoomFeedbackSerializer, HttpSuccessChatMessageReadSerializer, ListChatMessageHttpSuccessSerializer, ListChatRoomFeedbackResponseHttpSuccessResponseSerializer, ListChatRoomFeedbackResponseHttpSuccessSerializer,  ListReportChatroomReportHttpSuccessResposneSerializer, RetrieveChatRoomReportHttpSerializer, ReviewChatRoomFeedbackHttpErrorSerializer, ReviewChatRoomFeedbackHttpSuccessSerializer
from chat.models import ChatBot, ChatMessage,  ChatRoomFeedeback
from core.enums import QuerysetBranching, UserRole
from core.models import Therapist
from core.querysets import OwnedQS, PatientOwnedQS, QSWrapper
from core.viewssets import AugmentedViewSet, CustomPagination
from rest_framework.response import Response
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAdminUser
from drf_yasg.utils import swagger_auto_schema
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from jusoor_backend.settings import env
from sentiment_ai.agents.emotion_detector import MessageEmotionDetector
from sentiment_ai.tasks import calculate_sentiment

class ChatMessageViewset(AugmentedViewSet, ListModelMixin, RetrieveModelMixin, CreateModelMixin):
    """
        Viewset to view, list chat messages, and report chat messages
    """
    
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    filterset_fields = ['sender', 'receiver', 'created_at']
    pagination_class = CustomPagination
    action_permissions = {
        'list': [IsTherapist() | (IsPatient())],
        'retrieve': [IsTherapist() | (IsPatient())],
        'create': [IsPatient()],
    }

    serializer_class_by_action = {
        'list': ChatMessageReadSerializer,
        'retrieve': ChatMessageReadSerializer,
        'create': ChatMessageCreateSerializer,
    }

    # ownership queryset mapping
    queryset_by_action = {
        'list': QSWrapper(ChatMessage.objects.all()).branch( {
            UserRole.PATIENT.value: OwnedQS(ownership_fields=['sender', 'receiver']),
        }, by=QuerysetBranching.USER_GROUP, pass_through=[UserRole.THERAPIST.value]  ),
        'retrieve': QSWrapper(ChatMessage.objects.all()).branch( {
            UserRole.PATIENT.value: OwnedQS(ownership_fields=['sender', 'receiver']),
        }, by=QuerysetBranching.USER_GROUP, pass_through=[UserRole.THERAPIST.value]  ),
    }

    @swagger_auto_schema( responses={200: ListChatMessageHttpSuccessSerializer})
    def list(self, request, *args, **kwargs):
        """list the chat messages between users and chatbots
        """

        return super().list(request, *args, **kwargs)
    

    @swagger_auto_schema( responses={200: HttpSuccessChatMessageReadSerializer})
    def retrieve(self, request, *args, **kwargs):
        """retrieve the details of a certain chat message between a user and a chatbot
        
        ."""
        return super().retrieve(request, *args, **kwargs)
    
    
    @transaction.atomic
    @swagger_auto_schema( responses={200: HttpSuccessChatMessageReadSerializer, 400: HttpErrorCreateChatMessageSerializer})
    def create(self, request, *args, **kwargs):
        """send a message and get a responsew by the chatbot
        
        ."""

        # create the message
        bot = ChatBot.objects.get(id=ChatBot.objects.first().id)
        serializer: ChatMessageCreateSerializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.data

        user_message = ChatMessage.objects.create(
            sender=request.user,
            receiver=bot.user_profile,
            content=data['content']
            )

        # return a resposne from the chatbot
        agent = bot.get_agent(ChatGPTAgent if env('CONTEXT') != 'test' else DummyAIAgent)
        bot_message = agent.answer(
            user_id=request.user.id,
            message=data['content']

        )
        # create the bot message
        msg: ChatMessage = ChatMessage.objects.create(
            sender=bot.user_profile,
            receiver=request.user,
            content=bot_message.content
        )

        calculate_sentiment.delay(user_message.id)
        return Response( ChatMessageReadSerializer(msg).data, status=201)


# class ChatRoomViewset(AugmentedViewSet, ListModelMixin, RetrieveModelMixin, CreateModelMixin):
#     """
#         viewset used to manage chatroom, as well as feedbakc mechanism on the chatbot
#     """
    
#     ordering_fields = ['created_at']
#     filterset_fields = ['user', 'bot', 'last_updated_at']

#     action_permissions = {
#         'list': [IsTherapist() | IsPatient()],
#         'retrieve': [IsTherapist() | IsPatient()],
#         # 'create': [(IsPatient())],
#     }

#     serializer_class_by_action = {
#         'list': ChatRoomReadSerializer,
#         'retrieve': ChatRoomReadSerializer,
#         # 'create': ChatRoomCreateSerializer,
        
#     }

#     queryset_by_action = {
#         'list': QSWrapper(ChatRoom.objects.all()).branch( {
#             UserRole.PATIENT.value: OwnedQS(ownership_fields=['user']),
#         }, by=QuerysetBranching.USER_GROUP, pass_through=[UserRole.THERAPIST.value]  ),
#         'retrieve': QSWrapper(ChatRoom.objects.all()).branch( {
#             UserRole.PATIENT.value: OwnedQS(ownership_fields=['user']),
#         }, by=QuerysetBranching.USER_GROUP, pass_through=[UserRole.THERAPIST.value]  )
    
#     }

#     @swagger_auto_schema(responses= {200: ChatRoomListHttpResponseSuccessSerializer})
#     def list(self, request, *args, **kwargs):
#         """list the chat rooms between users and chatbots
        
#         ."""
#         return super().list(request, *args, **kwargs)
    
#     @swagger_auto_schema(responses= {200: ChatRoomRetrieveHttpSuccessSerializer})
#     def retrieve(self, request, *args, **kwargs):
#         """retrieve the details of a certain chat room between a user and a chatbot
        
#         .."""
#         return super().retrieve(request, *args, **kwargs)
    
#     # @swagger_auto_schema(responses= {200: CreateChatRoomReportHttpSuccessSerializer, 400: HttpErrorReportChatRoomFeedbackSerializer})
#     # def create(self, request, *args, **kwargs):
#     #     """create a new chatroom between authorizxed user and specified bot
        
#     #     ."""
#     #     return super().create(request, *args, **kwargs)
    

        


class ChatRoomFeedbackViewset(AugmentedViewSet, ListModelMixin, RetrieveModelMixin, CreateModelMixin):

    """
        Viewset to manage the feedback on the chat rooms
    """

    ordering_fields = ['created_at']
    filterset_fields = [ 'feedback', 'created_at']

    action_permissions = {
        'list': [ IsTherapist() | IsPatient()],
        'retrieve': [ IsTherapist() | IsPatient()],
        'create': [IsPatient()],
        'review': [IsTherapist()]
    }

    serializer_class_by_action = {
        'list': ChatRoomReportReadSerializer,
        'retrieve':  ChatRoomReportReadSerializer,
        'create': ReportChatroomCreateSerializer,
        'review': ReviewChatRoomFeedbackSerializer
    }

    queryset_by_action = {
        'list': QSWrapper(ChatRoomFeedeback.objects.all()).branch( {
            UserRole.PATIENT.value: OwnedQS(ownership_fields=['target_message__sender', 'target_message__receiver']),
        }, by=QuerysetBranching.USER_GROUP, pass_through=[UserRole.THERAPIST.value]  ),
        'retrieve': QSWrapper(ChatRoomFeedeback.objects.all()).branch( {
            UserRole.PATIENT.value: OwnedQS(ownership_fields=['target_message__sender', 'target_message__receiver']),
        }, by=QuerysetBranching.USER_GROUP, pass_through=[UserRole.THERAPIST.value]  ),
        'review': ChatRoomFeedeback.objects.all(),
    }

    @swagger_auto_schema(responses= {200: ListReportChatroomReportHttpSuccessResposneSerializer})
    def list(self, request, *args, **kwargs):
        """list feedbacks for given chat room messages by patients
        
        ."""
        return super().list(request, *args, **kwargs)
    
    
    @swagger_auto_schema(responses= {200: RetrieveChatRoomReportHttpSerializer})
    def retrieve(self, request, *args, **kwargs) -> Response:
        """retrieve the details of a certain chat room feedback
        
        ."""
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(responses= {200: CreateChatRoomReportHttpSuccessSerializer, 400: HttpErrorReportChatRoomFeedbackSerializer})
    def create(self, request, *args, **kwargs):
        """create a new chatroom between authorizxed user and specified bot
        
        ."""
        return super().create(request, *args, **kwargs)
    
    @swagger_auto_schema(responses= {200: ReviewChatRoomFeedbackHttpSuccessSerializer, 400: ReviewChatRoomFeedbackHttpErrorSerializer})
    @action(detail=True, methods=['post'])
    def review(self, request, *args, **kwargs):
        """endpoint to review the feedback of a chat room

        .
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        return Response(serializer.data, status=201)

class ChatRoomFeedbackResponseViewset(AugmentedViewSet, ListModelMixin, RetrieveModelMixin):

    """Viewset to manage the feedback on the chat rooms
    """

    ordering_fields = ['created_at']
    filterset_fields = ['feedback', 'created_at']

    action_permissions = {
        'list': [ IsPatient()],
        'retrieve': [ IsTherapist() | IsPatient()],
       
    }

    serializer_class_by_action = {
        'list': ChatRoomReportReadSerializer,
        'retrieve':  ChatRoomReportReadSerializer,

    }

    queryset_by_action = {
        'list': QSWrapper(ChatRoomFeedeback.objects.all()).branch( {
            UserRole.PATIENT.value: OwnedQS(ownership_fields=['target_message__sender', 'target_message__receiver']),
        }, by=QuerysetBranching.USER_GROUP, pass_through=[UserRole.THERAPIST.value]  ),
        'retrieve': QSWrapper(ChatRoomFeedeback.objects.all()).branch( {
            UserRole.PATIENT.value: OwnedQS(ownership_fields=['target_message__sender', 'target_message__receiver']),
        }, by=QuerysetBranching.USER_GROUP, pass_through=[UserRole.THERAPIST.value]  ),
    }

    @swagger_auto_schema(responses= {200: ListChatRoomFeedbackResponseHttpSuccessResponseSerializer })
    def list(self, request, *args, **kwargs):
        """list the chat room feedback responses

        .
        """
        return super().list(request, *args, **kwargs)
    
    
    @swagger_auto_schema(responses= {200: ListChatRoomFeedbackResponseHttpSuccessSerializer })
    def retrieve(self, request, *args, **kwargs) -> Response:
        """retrieve the details of a certain chat room feedback

        .
        """
        return super().retrieve(request, *args, **kwargs)

        

class ChatBotViewset(AugmentedViewSet, ListModelMixin, RetrieveModelMixin, CreateModelMixin, UpdateModelMixin):
    """
        Viewset to manage the different chatbot characters and their configurations
    """
    
    ordering_fields = ['created_at']

    action_permissions = {
        'list': [IsPatient() | IsTherapist() | IsAdminUser],
        'retrieve': [IsPatient() | IsTherapist() | IsAdminUser],
        'full_retrieve': [IsAdminUser],
        'create': [IsAdminUser],
        'update': [IsAdminUser],
        'partial_update': [IsAdminUser],

    }

    serializer_class_by_action = {
        'list': ChatBotReadSerializer,
        'retrieve': ChatBotReadSerializer,
        'full_retrieve': ChatBotFullReadSerializer,
        'create': ChatBotWriteSerializer,
        'update': ChatBotWriteSerializer,
        'partial_update': ChatBotWriteSerializer,

    }

    queryset = ChatBot.objects.all()

    @swagger_auto_schema(responses= {200: ChatBotListHttpSuccessResponseSerializer })
    def list(self, request, *args, **kwargs):
        """list all chatbots
        
        ."""
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(responses= {200: ChatBotRetrieveHttpSuccessSerializer })
    def retrieve(self, request, *args, **kwargs):
        """retrieve the details of a certain chatbot

        .
        """
        return super().list(request, *args, **kwargs)
    
    @swagger_auto_schema(responses= {200: ChatBotFullRetrieveHttpSuccessSerializer })
    def full_retrieve(self, request, *args, **kwargs):

        """fetches extenssive configurations of the chatbot

        .
        """
        return super().retrieve(request, *args, **kwargs)
    
    @swagger_auto_schema(responses= {200: ChatBotWriteSerializerSuccessSerializer })
    def create(self, request, *args, **kwargs):
        """create a new chatbot

            .
        """
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(responses= {200: ChatBotWriteSerializerSuccessSerializer })
    def update(self, request, *args, **kwargs):
        """update the chatbot configurations
        
        
        .
        """
        return super().update(request, *args, **kwargs)
    
    @swagger_auto_schema(responses= {200: ChatBotWriteSerializerSuccessSerializer(partial=True) })
    def partial_update(self, request, *args, **kwargs):
        """partially update the chatbot configurations
        
        
        .
        """
        return super().partial_update(request, *args, **kwargs)
    


