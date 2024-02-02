from django.db import models
from django.db.models import Q

from core.models import TimeStampedModel
from django.contrib.auth import get_user_model

# Create your models here.

class ChatMessage(TimeStampedModel):
    """
        Record for every message sent between 2 users in jusoor
    """

    content = models.TextField()
    sender = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, related_name='sent_messages')
    receiver = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, related_name='received_messages')


    @staticmethod
    def get_chat_history(user1, history_len: int = 8):
        """
            Method to get the chat history between 2 users

            @param user1: The used for whom the chat history is to be fetched
        """

        queryset= ChatMessage.objects.filter(Q(sender=user1) | Q(receiver=user1)).order_by('-created')    
        captured_len = max(history_len, queryset.count())

        return queryset[:captured_len]

class ChatBot(TimeStampedModel):
    """
        Model to store the chat bot configurations (useful for A/B testing multiple bots)
    """

    name = models.CharField(max_length=255, null=False, blank=False)
    user_profile = models.ForeignKey(get_user_model(), on_delete=models.PROTECT, related_name='bot_configurations')
    is_active = models.BooleanField(default=True)
    prompt = models.TextField() ## base prompt used by the bot
    captured_history_length = models.IntegerField(default=2) ## history length to be used by the bot
    response_len = models.IntegerField(default=100) # # max limit words emitted in response for the bot
    model_name = models.CharField(max_length=255, null=False, blank=False) ## model name to be used by the bot 

    def __str__(self):
        return self.name