
from django.db import models

from core.models import StudentPatient, Therapist, TimeStampedModel
from surveys.enums import PENDING, SURVEY_QUESTION_TYPES, SURVEY_RESPONSE_STATUSES
from rest_framework.exceptions import ValidationError

from surveys.types import MultipleChoiceQuestionBodySchema, TextOnlyQuestionBodySchema
from surveys.utils.validation import TherapistSurveyValidators
# Create your models here.
from django.db import transaction
class TherapistSurvey(TimeStampedModel):

    # TODO: add a survey description
    created_by = models.ForeignKey(Therapist, null=False, on_delete=models.PROTECT, related_name='created_surveys')
    last_updated_by = models.ForeignKey(Therapist, null=True, on_delete=models.PROTECT, related_name='updated_surveys')
    name = models.CharField(max_length=255, null=False, unique=True)
    description = models.TextField(null=False, blank=False)
    image = models.ImageField(upload_to='surveys/', null=True, blank=True)
    active = models.BooleanField(default=False) ## used to activate or deactivate the survey
    def __str__(self):
        return f'{self.name} - by {self.created_by}'
    
    def publish(self):
        pass
    

## WARNING: no question should be created unless its schema is validated through the appropriate pydantic validator
class TherapistSurveyQuestion(TimeStampedModel):
    survey = models.ForeignKey(TherapistSurvey, null=False, on_delete=models.CASCADE, related_name='questions')
    description = models.TextField(null=False)
    # TODO: rename to type
    question_type = models.CharField(choices=SURVEY_QUESTION_TYPES.items(), max_length=255, null=False, default='text')
    # TODO: force it to be required
    schema = models.JSONField(null=False, blank=True)
    active = models.BooleanField(default=True) ## used to activate or deactivate the survey
    index = models.PositiveIntegerField(null=False) ## used to order the questions in the survey
    image = models.ImageField(upload_to='survey-questions/', null=True, blank=True)
    def __str__(self):
        return f'Q#{self.index}: {self.description}  -> survey #{self.survey.pk}'

    def correct_ordering_index(self, incoming_index: int) -> int:
        """
            validate and assign a corrected index for the question to avoid indeixing holes
        """
        old_index = TherapistSurveyQuestion.objects.get(pk=self.pk).index if self.pk else None

        # if the incoming index is exceeding question number or is newly created, assign it the latest index
        if incoming_index == None or incoming_index > self.survey.questions.filter(index__isnull=False).count() + 1 or self.survey.questions.filter(index__isnull=False).count() == 0:
            incoming_index = self.survey.questions.filter(index__isnull=False).count() + 1
        # if there is a question with the same index in the same survey, increment the index of all questions with index >= self.index
        elif TherapistSurveyQuestion.objects.filter(survey=self.survey, index=incoming_index).exists():
            
            # if the question is new, simply push everything to the back without caring about old index holes
            if old_index == None:
                TherapistSurveyQuestion.objects.filter(survey=self.survey, index__gte=incoming_index).update(index=models.F('index') + 1)

            # if we advance the idnex forwards, we need all items in between to be shifted to the back
            elif old_index < incoming_index:
                TherapistSurveyQuestion.objects.filter(survey=self.survey, index__lte=incoming_index, index__gt=old_index).update(index=models.F('index') - 1)
            
            # if we re-order the question to the back, we simply increment the index of all questions with larger index than the
            # the new index and smaller than the old index by 1 to avoid holes
            elif old_index > incoming_index:
                TherapistSurveyQuestion.objects.filter(survey=self.survey, index__gte=incoming_index, index__lt=old_index).update(index=models.F('index') + 1)
        

        
        return incoming_index

    @transaction.atomic()
    def save(self, *args, **kwargs) -> None:
        
        if hasattr(self, 'schema') and self.schema != None:
            TherapistSurveyValidators.validate_question_schema(self.schema, self.question_type)

        self.index = self.correct_ordering_index(self.index)
        
        return super().save(*args, **kwargs)
    
    class Meta:
        unique_together = [['survey', 'index'], ['survey', 'description']]

class TherapistSurveyResponse(TimeStampedModel):
    """
        grouping used to link a group of question resposned for one survey at once
        (because the survey can be taken multiple times by the same patient)
    """
    survey = models.ForeignKey(TherapistSurvey, null=False, on_delete=models.CASCADE, related_name='responses')
    patient = models.ForeignKey(StudentPatient, null=False, on_delete=models.CASCADE, related_name='survey_response_patients')
    status = models.CharField(choices=SURVEY_RESPONSE_STATUSES.items(), max_length=255, default=PENDING)
    
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
    
    def save(self, *args, **kwargs) -> None:
        
        TherapistSurveyValidators.validate_answer_schema({'answer': self.answer}, self.question.question_type)
        
        return super().save(*args, **kwargs)
    
    class Meta:
        unique_together = [['survey_response', 'question']]