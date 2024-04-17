from celery import shared_task

from authentication.models import User
from chat.enums import PENDING
from chat.models import ChatMessage
from sentiment_ai.agents.emotion_detector import MessageEmotionDetector
from sentiment_ai.agents.report_generator import SentimentReportGenerator
from sentiment_ai.models import MessageSentiment, SentimentReport, StudentPatientSentimentPosture
from sentiment_ai.types import SentimentEval
from django.utils import timezone

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

@shared_task
def generate_reports(user_id: int):
    """
        generating an automated report for the patient using his chat history
    """

    # get an answer for the patient history
    user= User.objects.select_related('patient_profile').get(pk=user_id)
    # create the report resposne from the LLM
    agent = SentimentReportGenerator()
    sentiment_score, message_sentiments = SentimentReport.calculate_batch_message_sentiment(user)

    report = SentimentReport(status=PENDING, patient=user.patient_profile, sentiment_score=sentiment_score)
    result = agent.answer(user, report)

    # save the report response
    report.conversation_highlights=result.conversation_highlights,
    report.recommendations=result.recommendations,
    report.save()
    # link the message sentiments to the report

    sentiment_report_links = []
    for message_sentiment in message_sentiments:
        sentiment_report_links.append(MessageSentiment(sentiment_report=report, message=message_sentiment ))

    MessageSentiment.objects.bulk_create(sentiment_report_links)

    return report.pk
