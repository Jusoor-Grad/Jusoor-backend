import decimal
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from chat.models import ChatMessage
from core.db.fields import ZeroToOneDecimalField
from core.models import StudentPatient, TimeStampedModel
from django.utils import timezone

from sentiment_ai.types import SentimentEval

# Create your models here.

class SentimentReport(TimeStampedModel):
    """
        models the creationg of an on-demand sentiment report for the patient
    """

    patient = models.ForeignKey(StudentPatient, on_delete=models.CASCADE, related_name='sentiment_reports')
    sentiment_analysis = models.TextField()
    conversation_highlights = models.TextField()
    recommendations = models.TextField()
    sentiment_score = ZeroToOneDecimalField()
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()


class MessageSentiment(TimeStampedModel):
    """
        storing the individual sentiment results for each message
        NOTE: the sentiment results for each
    """

    message = models.OneToOneField(ChatMessage, on_delete=models.CASCADE, related_name='sentiment_result', unique=True)
    sad = ZeroToOneDecimalField()
    joy = ZeroToOneDecimalField()
    # love = ZeroToOneDecimalField()
    fear = ZeroToOneDecimalField()
    anger = ZeroToOneDecimalField()
    surprise = ZeroToOneDecimalField()


class ReportSentimentMessage(TimeStampedModel):
    """storing the includision of a message sentiment result within a report"""
    report = models.ForeignKey(SentimentReport, on_delete=models.CASCADE, related_name='sentiment_messages')
    message = models.ForeignKey(MessageSentiment, on_delete=models.CASCADE, related_name='sentiment_reports')
    sentiment_score = ZeroToOneDecimalField()

class StudentPatientSentimentPosture(models.Model):
    patient = models.ForeignKey(StudentPatient, on_delete=models.PROTECT, related_name='sentiment_postures')
    date = models.DateField(null=False, blank=False)
    score = ZeroToOneDecimalField() ## how positive is the patient feeling

    @staticmethod
    def update_sentiment( patient: StudentPatient, sentiment_reading: SentimentEval):

        

        # get the posture score for the patient
        posture_score, posture_created = StudentPatientSentimentPosture.objects.get_or_create(defaults={
            'patient': patient,
            'date': timezone.now().date(),
            'score': 0.5
        }, patient=patient, date=timezone.now().date())

        if posture_created:
            last_score = StudentPatientSentimentPosture.objects.filter(patient=patient).order_by('date').filter(date__lt=timezone.now()).last()
            posture_score.score = last_score.score * decimal.Decimal(0.95) if last_score else 0.5

        # update the sentiment using an exponential weighted average of the attributes of the prediction
        new_score_weight = decimal.Decimal(0.65)

        # weight contribution of each feeling
        positive_score = sentiment_reading.joy * 0.5 + sentiment_reading.love * 0.5
        negative_score = sentiment_reading.sad *  0.4 + sentiment_reading.fear * 0.3 + sentiment_reading.anger * 0.3
        # surpirse can be either positive or negative, so we will weight it by the difference between the positive and negative scores
        surprise_factor = (positive_score - negative_score) * sentiment_reading.surprise
        # clipping the posture score in the region of [0-1]
        new_raw_score = max(0.15, min(1, (positive_score * 1.5 - negative_score * 0.7) + surprise_factor * 0.5 )) 
        # update the moving average of the patient score

        posture_score.score = posture_score.score * (1 - new_score_weight) + decimal.Decimal(new_raw_score) * new_score_weight
        posture_score.save()

        return posture_score

    class Meta:
        unique_together = ('patient', 'date')
        ordering = ('-date',)
