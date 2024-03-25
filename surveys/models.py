import copy
from enum import unique
from msilib import schema
from typing import Iterable
from django.db import models

from core.models import StudentPatient, Therapist, TimeStampedModel
from surveys.enums import SURVEY_QUESTION_TYPES, SURVEY_RESPONSE_STATUSES, SurveyQuestionTypes
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from surveys.types import MultipleChoiceQuestionBodySchema, TextOnlyQuestionBodySchema
from surveys.utils.validation import TherapistSurveyValidators
# Create your models here.

class TherapistSurvey(TimeStampedModel):

    created_by = models.ForeignKey(Therapist, null=False, on_delete=models.PROTECT, related_name='created_surveys')
    last_updated_by = models.ForeignKey(Therapist, null=True, on_delete=models.PROTECT, related_name='updated_surveys')
    name = models.CharField(max_length=255, null=False, unique=True)
    image = models.ImageField(upload_to='surveys/', null=True, blank=True)
    active = models.BooleanField(default=False) ## used to activate or deactivate the survey
    def __str__(self):
        return f'{self.name} - by {self.created_by}'
    
    def publish(self):
        pass
    

class TherapistSurveyQuestion(TimeStampedModel):
    survey = models.ForeignKey(TherapistSurvey, null=False, on_delete=models.CASCADE, related_name='questions')
    description = models.TextField(null=False)
    question_type = models.CharField(choices=SURVEY_QUESTION_TYPES.items(), max_length=255, null=False, default='text')
    schema = models.JSONField(null=True, blank=True)
    active = models.BooleanField(default=True) ## used to activate or deactivate the survey
    index = models.IntegerField(default=0) ## used to order the questions in the survey
    image = models.ImageField(upload_to='survey-questions/', null=True, blank=True)
    def __str__(self):
        return f'{self.question} - {self.survey}'

    def save(self, force_insert: bool = ..., force_update: bool = ..., using: str | None = ..., update_fields: Iterable[str] | None = ...) -> None:
        
        if hasattr(self, 'schema') and self.schema != None:
            TherapistSurveyValidators.validate_question_schema(self.schema, self.question_type)
            
        return super().save(force_insert, force_update, using, update_fields)
    
    class Meta:
        unique_together = [['survey', 'index'], ['survey', 'description']]

class TherapistSurveyResponse(TimeStampedModel):
    """
        grouping used to link a group of question resposned for one survey at once
        (because the survey can be taken multiple times by the same patient)
    """
    survey = models.ForeignKey(TherapistSurvey, null=False, on_delete=models.CASCADE, related_name='responses')
    patient = models.ForeignKey(StudentPatient, null=False, on_delete=models.CASCADE, related_name='survey_response_patients')
    status = models.CharField(choices=SURVEY_RESPONSE_STATUSES.items(), max_length=255, default='PENDING')
    
    def __str__(self):
        return f'Survey resposne group identiifer #{self.survey} for {self.patient}'
    

class TherapistSurveyQuestionResponse(TimeStampedModel):
    """
        used to store the resposne of the patient to the survey for a single question
    """

    # grouping field to indicate which group resposne was this question response part of
    survey_response = models.ForeignKey(TherapistSurveyResponse, null=False, on_delete=models.CASCADE, related_name='response_answers')
    survey = models.ForeignKey(TherapistSurvey, null=False, on_delete=models.CASCADE, related_name='survey_response_answers')
    question = models.ForeignKey(TherapistSurveyQuestion, null=False, on_delete=models.CASCADE, related_name='question_response_answers')
    answer = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f'Patient answer for {self.question} - {self.survey_response}'
    
    def save(self, force_insert: bool = ..., force_update: bool = ..., using: str | None = ..., update_fields: Iterable[str] | None = ...) -> None:
        
        TherapistSurveyValidators.validate_answer_schema(self.answer, self.question.question_type)
        
        return super().save(force_insert, force_update, using, update_fields)