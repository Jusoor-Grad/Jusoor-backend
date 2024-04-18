from calendar import c
import faker
from typing import Dict
from django.db import transaction
from authentication.models import User
from chat.enums import PENDING
from chat.mock import ChatBotMocker, ChatMessageMocker
from chat.models import ChatMessage
from core.mock import UserMock, PatientMock
from sentiment_ai.enums import FAILED
from sentiment_ai.models import MessageSentiment, ReportSentimentMessage, SentimentReport
from surveys.enums import COMPLETED



class MessageSentimentMocker:

    @transaction.atomic
    def mock_instances(n: int, msg_fixed_args: Dict = dict(), sent_fixed_args: Dict = dict()):
        
        # mock messages
        messages = ChatMessageMocker.mock_instances(n // 2, **msg_fixed_args)
        fake = faker.Faker()

        sentiments = [ ]
        # mock message sentiments
        for msg in messages:

            if not msg.sender.is_bot:
                sentiment = MessageSentiment(
                    **{'message':msg,
                    'sad': fake.random.random(),
                    'joy': fake.random.random(),
                    'fear': fake.random.random(),
                    'anger': fake.random.random(),
                    'surprise': fake.random.random(),
                    **sent_fixed_args   
                    },
                )
                sentiments.append(sentiment)

        return MessageSentiment.objects.bulk_create(sentiments)

class SentimentReportMocker:

    @transaction.atomic
    @staticmethod
    def mock_instances(n: int = 1, n_messages = 10, fixed_user: User = None, report_fixed_arg: Dict = dict(), msg_sentiment_fixed_args: Dict = dict):


        fake = faker.Faker()

        # fake n patients
        patients = PatientMock.mock_instances(n) if not fixed_user else [fixed_user.patient_profile]
        # fake a bot user
        bot_user = ChatBotMocker.mock_instances(n=1)[0]
        # mock message sentiments
        message_sent_timelines =  [ MessageSentimentMocker.mock_instances(n_messages, msg_fixed_args={'user': p.user, 'bot':bot_user}) for p in patients]

        reports = []
        message_sentiment_reports = []
        for i in range(n):
            
            report = SentimentReport(
                    **{'patient':patients[i],
                    'conversation_highlights': fake.paragraph(),
                    'recommendations': fake.paragraph(),
                    'sentiment_score': fake.random.random(),
                    'status': fake.random.choice([PENDING, COMPLETED, FAILED]),
                    **report_fixed_arg  
                })
            
            for msg in message_sent_timelines[i]:
                
                message_sentiment_reports.append(
                    ReportSentimentMessage(
                        report=report,
                        message=msg,
                    )
                )

            report.report_ending_message = message_sentiment_reports[-1].message.message
            
            reports.append(report)
        
        reports = SentimentReport.objects.bulk_create(reports)

        message_sentiment_reports = ReportSentimentMessage.objects.bulk_create(message_sentiment_reports)

        return reports, message_sentiment_reports

@transaction.atomic        
def run():

    msgs = ChatMessage.objects.filter(sender__pk=137)
    fake = faker.Faker() 
    sents = []

    for msg in msgs:    
        sent = MessageSentiment(
            message=msg,
            sad = fake.random.random(),
            joy = fake.random.random(),
            fear = fake.random.random(),
            anger = fake.random.random(),
            surprise = fake.random.random()
        )
        sents.append(sent)

    MessageSentiment.objects.bulk_create(sents)
    print('done')



