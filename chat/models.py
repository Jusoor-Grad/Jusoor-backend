from django.db import models
from django.db.models import Q
from chat.enums import FEEDBACK_STATUSES

from core.models import StudentPatient, Therapist, TimeStampedModel
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator


class ChatBot(TimeStampedModel):
    """
        Model to store the chat bot configurations (useful for A/B testing multiple bots and possible give multiple bot personalities)
    """

    name = models.CharField(max_length=255, null=False, blank=False)
    user_profile = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, related_name='bot_profile')
    is_active = models.BooleanField(default=True)
    prompt = models.TextField() ## base prompt used by the bot
    temperature = models.DecimalField(default=0.7, decimal_places=2, max_digits=3, validators = [MinValueValidator(0.01), MaxValueValidator(1)]) ## temperature to be used by the bot
    captured_history_length = models.IntegerField(default=2) ## history length to be used by the bot
    max_response_tokens = models.IntegerField(default=100) # # max limit words emitted in response for the bot
    model_name = models.CharField(max_length=255, null=False, blank=False) ## model name to be used by the bot 
    top_p =  models.DecimalField(default=0.7, decimal_places=2, max_digits=3, validators = [MinValueValidator(0.01), MaxValueValidator(1)])


    def __str__(self):
        return self.name
    
    def get_agent(self, agent_cls):
        return agent_cls(**self.get_config())
    
    def get_config(self):
        """
            Method to get the bot configuration
        """

        return {
            'temperature': self.temperature,
            'max_response_tokens': self.max_response_tokens,
            'model_name': self.model_name,
            'top_p': self.top_p,
            'history_len': self.captured_history_length,
            'prompt': self.prompt
            
        }

# TODO: we might add sentiment analysis to the chat rooms    
# class ChatRoom(TimeStampedModel):
#     """
#         record to save the chat rooms between a user and certain bot characters
#         we may use it in the future to create aggregate sentiment stats of the user
#         interactions within each room
#     """

#     user = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, related_name='chat_rooms')
#     bot = models.ForeignKey(ChatBot, on_delete=models.PROTECT, related_name='bot_rooms')

#     def __str__(self):
#         return f'{self.user} - {self.bot}'
    
#     def get_agent(self, agent_cls):
#         """
#             Method to get the chatbot agent
#         """

#         return self.bot.get_agent(agent_cls)

class ChatMessage(TimeStampedModel):
    """
        Record for every message sent between 2 users in jusoor
    """

    content = models.TextField()
    sender = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, related_name='sent_messages')
    receiver = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, related_name='received_messages')
    # chat_room = models.ForeignKey(ChatRoom, on_delete=models.PROTECT, related_name='messages')
    read = models.BooleanField(default=False)


    @staticmethod
    def get_chat_history(user1, history_len: int = 8):
        """
            Method to get the chat history between 2 users

            @param user1: The used for whom the chat history is to be fetched
        """

        queryset= ChatMessage.objects.filter(Q(sender=user1) | Q(receiver=user1)).order_by('-created')    
        captured_len = max(history_len, queryset.count())

        return queryset[:captured_len]
    

class ChatRoomFeedeback(TimeStampedModel):

    patient = models.ForeignKey(StudentPatient, on_delete=models.PROTECT, related_name='feedbacks')
    status = models.CharField(choices=FEEDBACK_STATUSES.items(), default='PENDING', max_length=255)
    feedback = models.TextField() # feedback from the patient
    # specifiyng the range of messages to be reported
    target_message = models.ForeignKey(ChatMessage, on_delete=models.PROTECT, related_name='message_feedbacks')
    

class ChatRoomFeedbackResponse(TimeStampedModel):
    """
        Model to store the feedback response from the therapist
    """

    feedback = models.ForeignKey(ChatRoomFeedeback, on_delete=models.PROTECT, related_name='responses')
    therapist = models.ForeignKey(Therapist, on_delete=models.PROTECT, related_name='feedback_responses')
    response = models.TextField() # response from the therapist
