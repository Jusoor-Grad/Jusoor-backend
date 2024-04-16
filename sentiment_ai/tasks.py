from celery import shared_task

from chat.models import ChatMessage
from sentiment_ai.agents.emotion_detector import MessageEmotionDetector
from sentiment_ai.models import MessageSentiment, StudentPatientSentimentPosture
from sentiment_ai.types import SentimentEval


@shared_task
def calculate_sentiment(message_id: int):
    """
    This function will be called by celery to calculate the sentiment of a message
    """

    # get the message from the database
    message = ChatMessage.objects.get(pk=message_id)

    # get the sentiment of the message
    sentiment: SentimentEval = MessageEmotionDetector().predict(message).prediction

    # create a message sentiment object
    message_sentiment=  MessageSentiment.objects.create(
        message=message,
        sad=sentiment.sad,
        joy=sentiment.joy + sentiment.love,
        fear=sentiment.fear,
        anger=sentiment.anger,
        surprise=sentiment.surprise
    )

    # update the user daily sentiment profile
    new_posture = StudentPatientSentimentPosture.update_sentiment(patient=message.sender.patient_profile, sentiment_reading=sentiment)
    print('NEW POSTURE SCORE: ', new_posture.score)

    return message_sentiment.pk
        