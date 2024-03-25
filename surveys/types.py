from pyexpat import model
from pydantic import BaseModel, model_validator
from typing import List, Optional, Generic, TypeVar, Union
from django.utils.translation import gettext_lazy as _

from surveys.enums import SurveyQuestionTypes

QuestionSchema = TypeVar('QuestionSchema')
AnswerSchema = TypeVar('AnswerSchema')


class MultipleChoiceQuestionBodySchema(BaseModel):
    """
        Type for the form of the multiple choice question
    """
    options: List[str]
    allow_multiple: bool

    @model_validator(mode='after')
    def validate_options(cls, data):

        if len(data.options) < 2:
            raise ValueError(_('Must have at least 2 options'))
        return data
    

class MultipleChoiceFieldAnswerSchema(BaseModel):
    """Representation of the answer to a multiple choice question"""
    
    answer: List[int] # list of indices chosen by the user
    allow_multiple: bool

    @model_validator(mode='after')
    def validate_answer(cls, data):
        if len(data.answer) < 1:
            raise ValueError(_('Must have at least 1 answer'))
        
        if len(data.answer) > 1 and not data.allow_multiple:
            raise ValueError(_('Only one answer is allowed'))
        return data

class TextOnlyQuestionBodySchema(BaseModel):
    max_length: Optional[int] = 300
    min_length: Optional[int] = 10

    @model_validator(mode='after')
    def validate_max_length(cls, data):
        if data.max_length and data.min_length and data.max_length < data.min_length:
            raise ValueError(_('Max length must be greater than min length'))
        return data



class TextOnlyFieldAnswerSchema(BaseModel):
    """Representation of the answer to a text only question"""
    answer: str