from celery import shared_task
from sqlalchemy import Transaction
from contextlib import suppress
from authentication.models import User
from chat.enums import PENDING
from chat.mock import ChatBotMocker
from chat.models import ChatMessage
from core.mock import PatientMock, UserMock
from sentiment_ai.agents.emotion_detector import EmotionDetector
from sentiment_ai.agents.mental_disorder_detector import MentalDisorderDetector
from sentiment_ai.agents.report_generator import SentimentReportGenerator
from sentiment_ai.enums import COMPLETED, FAILED
from sentiment_ai.mock import MessageSentimentMocker, SentimentReportMocker
from sentiment_ai.models import MessageSentiment, ReportSentimentMessage, SentimentReport, StudentPatientSentimentPosture
from sentiment_ai.types import SentimentEval
from django.utils import timezone
from django.db import transaction
from langchain_core.exceptions import OutputParserException
from datetime import datetime

@shared_task
@transaction.atomic
def calculate_sentiment(message_id: int):
    """
    This function will be called by celery to calculate the sentiment and possibility of mental disorder within a message
    """

    # get the message from the database
    message = ChatMessage.objects.get(pk=message_id)

    # get the sentiment of the message
    sentiment: SentimentEval = EmotionDetector().predict(message).prediction
    mental_disorder_prediction = MentalDisorderDetector().predict(message.content)
    print(mental_disorder_prediction)
    # create a message sentiment object
    message_sentiment=  MessageSentiment.objects.create(
        message=message,
        sad=sentiment.sad,
        joy=sentiment.joy + sentiment.love,
        fear=sentiment.fear,
        anger=sentiment.anger,
        surprise=sentiment.surprise,
        **mental_disorder_prediction.model_dump()
    )

    # update the user daily sentiment profile
    new_posture = StudentPatientSentimentPosture.update_sentiment(patient=message.sender.patient_profile, sentiment_reading=sentiment)
    print('NEW POSTURE SCORE: ', new_posture.score)

    return message_sentiment.pk


@shared_task
@transaction.atomic
def generate_sentiment_report(user_id: int, start_at: datetime, end_at: datetime):
    """
        generating an automated report for the patient using his chat history

        @param user_id: the user id of the patient requesting the report
    """

    # get an answer for the patient history
    user= User.objects.select_related('patient_profile').get(pk=user_id)
    # create the report resposne from the LLM
    agent = SentimentReportGenerator()
    captured_messages = ChatMessage.objects.filter(sender=user, created_at__gte=start_at, created_at__lte=end_at)
    print(len(captured_messages))
    sentiment_score, message_sentiments = SentimentReport.calculate_batch_message_sentiment(latest_messages=captured_messages)
    mental_disorder_score = SentimentReport.get_cumulative_mental_disorder_score(captured_messages)
    try:
        result = agent.answer(user, messages=captured_messages)
    except OutputParserException as e:
            report.status = FAILED
            report.save()
            print('FAILED 3 TIMES')
            raise ValueError("LLM failed to generate a report for the patient after 3 failing trials") from e


    # save the report response
    report = SentimentReport.objects.create(
        status=PENDING, patient=user.patient_profile, sentiment_score=sentiment_score,
        conversation_highlights=result.conversation_highlights,
        recommendations=result.recommendations,
        **mental_disorder_score
    )
    # link the message sentiments included to the report

    sentiment_report_links = []
    for message_sentiment in message_sentiments:
        sentiment_report_links.append(ReportSentimentMessage(report=report, message=message_sentiment ))

    ReportSentimentMessage.objects.bulk_create(sentiment_report_links)

    report.status = COMPLETED
    report.save()
    print('REPORT GENERATED SUCCESSFULLY')
    return report.pk


@transaction.atomic
def run():
    """side-code to test the sentiment report generation task without affecting the DB"""

    # mock sentiment messages with existing report
     
    generate_sentiment_report(137)
