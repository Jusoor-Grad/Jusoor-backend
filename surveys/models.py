from django.db import models

from core.models import StudentPatient, Therapist, TimeStampedModel

# Create your models here.

class TherapistSurvey(TimeStampedModel):

    therapist = models.ForeignKey(Therapist, null=False, on_delete=models.PROTECT)
    name = models.CharField(max_length=255, null=True)
    image = models.ImageField(upload_to='surveys/', null=True, blank=True)
    active = models.BooleanField(default=False) ## used to activate or deactivate the survey
    ready_to_publish = models.BooleanField(default=False) ## used to indicate if the survey is ready to be published
    def __str__(self):
        return f'{self.name} - by {self.therapist}'

class TherapistSurveyQuestion(TimeStampedModel):
    survey = models.ForeignKey(TherapistSurvey, null=False, on_delete=models.CASCADE)
    description = models.TextField(null=True)
    # TODO: create a custom validator to be sued for enum char fields
    question_type = models.CharField(max_length=255, null=False, default='text')
    # TODO: inject pydantic validation based on the value of question_type
    answer = models.JSONField(null=True, blank=True)
    active = models.BooleanField(default=False) ## used to activate or deactivate the survey
    ready_to_publish = models.BooleanField(default=False) ## used to indicate if the survey is ready to be published

    def __str__(self):
        return f'{self.question} - {self.survey}'
    

class TherapistSurveyResponse(TimeStampedModel):
    """
        grouping used to link a group of question resposned for one survey at once
        (because the survey can be taken multiple times by the same patient)
    """
    survey = models.ForeignKey(TherapistSurvey, null=False, on_delete=models.CASCADE, related_name='responses')
    patient = models.ForeignKey(StudentPatient, null=False, on_delete=models.CASCADE, related_name='survey_response_patients')
    def __str__(self):
        return f'Survey resposne group identiifer #{self.survey} for {self.patient}'
    

class TherapistSurveyQuestionResponse(TimeStampedModel):
    """
        used to store the resposne of the patient to the survey for a single question
    """
    survey_response = models.ForeignKey(TherapistSurveyResponse, null=False, on_delete=models.CASCADE, related_name='response_answers')
    survey = models.ForeignKey(TherapistSurvey, null=False, on_delete=models.CASCADE, related_name='survey_response_answers')
    question = models.ForeignKey(TherapistSurveyQuestion, null=False, on_delete=models.CASCADE, related_name='question_response_answers')
    answer = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f'Patient answer for {self.question} - {self.survey_response}'