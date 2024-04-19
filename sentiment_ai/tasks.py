from celery import shared_task
from sqlalchemy import Transaction
from contextlib import suppress
from authentication.models import User
from chat.enums import PENDING
from chat.mock import ChatBotMocker
from chat.models import ChatMessage
from core.mock import PatientMock, UserMock
from sentiment_ai.agents.emotion_detector import MessageEmotionDetector
from sentiment_ai.agents.report_generator import SentimentReportGenerator
from sentiment_ai.enums import COMPLETED, FAILED
from sentiment_ai.mock import MessageSentimentMocker, SentimentReportMocker
from sentiment_ai.models import MessageSentiment, ReportSentimentMessage, SentimentReport, StudentPatientSentimentPosture
from sentiment_ai.types import SentimentEval
from django.utils import timezone
from django.db import transaction
from langchain_core.exceptions import OutputParserException

@shared_task
@transaction.atomic
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
@transaction.atomic
def generate_sentiment_report(user_id: int):
    """
        generating an automated report for the patient using his chat history

        @param user_id: the user id of the patient requesting the report
    """

    # get an answer for the patient history
    user= User.objects.select_related('patient_profile').get(pk=user_id)
    # create the report resposne from the LLM
    agent = SentimentReportGenerator()
    sentiment_score, message_sentiments = SentimentReport.calculate_batch_message_sentiment(user)

    try:
        result = agent.answer(user)
    except OutputParserException as e:
            report.status = FAILED
            report.save()
            raise ValueError("LLM failed to generate a report for the patient after 3 failing trials") from e


    # save the report response
    report = SentimentReport.objects.create(
        status=PENDING, patient=user.patient_profile, sentiment_score=sentiment_score,
        conversation_highlights=result.conversation_highlights,
        recommendations=result.recommendations,
        report_ending_message= message_sentiments.order_by('-created_at')[0].message
    )
    # link the message sentiments included to the report

    sentiment_report_links = []
    for message_sentiment in message_sentiments:
        sentiment_report_links.append(ReportSentimentMessage(report=report, message=message_sentiment ))

    ReportSentimentMessage.objects.bulk_create(sentiment_report_links)

    report.status = COMPLETED
    report.save()

    return report.pk


@transaction.atomic
def run():
    """side-code to test the sentiment report generation task without affecting the DB"""

    # mock sentiment messages with existing report
    patient = PatientMock.mock_instances(1)[0]
    bot  = ChatBotMocker.mock_instances(1)[0]
    report = SentimentReportMocker.mock_instances(n_messages=14)[0][0]

    # mock  sentiment messages with no report
    print(bot.user_profile.is_bot)
    no_report_msgs = MessageSentimentMocker.mock_instances(10, msg_fixed_args={'user': patient.user, 'bot': bot})
    # mock the batch message sentiment

    print(len(no_report_msgs), len(ReportSentimentMessage.objects.filter(report=report)))
    
    # create a new actual report
    new_report_id = generate_sentiment_report(patient.user.id)

    
    print('REPORTED MESSAGES AFTER', len(ReportSentimentMessage.objects.filter(report=new_report_id)))
    
    raise RuntimeError("TERMINATED")
