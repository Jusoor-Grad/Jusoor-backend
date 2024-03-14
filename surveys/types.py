from pyexpat import model
from pydantic import BaseModel, model_validator
from typing import List, Optional, Generic, TypeVar, Union
from django.utils.translation import gettext_lazy as _

QuestionResposneSchema = TypeVar('QuestionResposneSchema')


class MultipleChoiceAnswerSchema(BaseModel):
    options: List[str]
    allow_multiple: bool

    @model_validator(mode='after')
    def validate_options(cls, data):
        if len(data['options']) < 2:
            raise ValueError(_('Must have at least 2 options'))
        return data

class MultipleChoiceAnswerRawRespsonse(BaseModel):
    schema_question_id = int
    answer: List[str]


    @model_validator(mode='after')
    def validate_answer(cls, data):
        if len(data['answer']) < 1:
            raise ValueError(_('Must have at least 1 answer'))
        
        if len(data['answer']) > 1 and not data['allow_multiple']:
            raise ValueError(_('Only one answer is allowed'))
        return data

class TextOnlyAnswerSchema(BaseModel):
    max_length: Optional[int] 
    min_length: Optional[int] = 10

    @model_validator(mode='after')
    def validate_max_length(cls, data):
        if data['max_length'] and data['min_length'] and data['max_length'] < data['min_length']:
            raise ValueError(_('Max length must be greater than min length'))
        return data
    
class TextOnlyAnswerRawResponse(BaseModel):
    schema_question_id: int
    answer: str

class SurveyQuestion(BaseModel, Generic[QuestionResposneSchema]):
    id: int
    question: str
    image: Optional[str]
    type: QuestionResposneSchema


class SurveyQuestionFullResponse(BaseModel, Generic[QuestionResposneSchema]):
    response: QuestionResposneSchema
    question: SurveyQuestion[QuestionResposneSchema]
    

class TherapistSurvey(BaseModel):
    name: str
    description: str
    questions: List[SurveyQuestion]


GenericSurveyQuestion = SurveyQuestion[Union[MultipleChoiceAnswerSchema, TextOnlyAnswerSchema]]
RawSurveyAnswer = Union[MultipleChoiceAnswerRawRespsonse, TextOnlyAnswerRawResponse]

class TherapistSurveyRawResponse(BaseModel):
    therapist_survey_id: int
    answers: List[RawSurveyAnswer]
    @model_validator(mode='after')
    def validate_answers(cls, data):
        survey = TherapistSurvey.objects.get(id=data['therapist_survey_id'])
        if len(data['answers']) != len(survey.questions):
            raise ValueError(_('All questions must be answered'))
        return data
    
