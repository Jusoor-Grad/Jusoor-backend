

import copy
from surveys.enums import SurveyQuestionTypes
from surveys.types import MultipleChoiceFieldAnswerSchema, MultipleChoiceQuestionBodySchema, TextOnlyFieldAnswerSchema, TextOnlyQuestionBodySchema
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class TherapistSurveyValidators:


    @staticmethod
    def validate_question_schema(schema: dict, question_type: SurveyQuestionTypes):
        try:
            if question_type == SurveyQuestionTypes.TEXT.value:
                data = copy.deepcopy(schema)
                TextOnlyQuestionBodySchema(**data)
            elif question_type ==  SurveyQuestionTypes.MULTIPLE_CHOICE.value:
                data = copy.deepcopy(schema)
                MultipleChoiceQuestionBodySchema(**data)
            else:
                raise ValidationError(_("Invalid question type"))
        except Exception as e:
            raise ValidationError(_("Invalid question schema for the specified question type"))
        
    @staticmethod
    def validate_answer_schema(schema: dict, question_type: SurveyQuestionTypes):
        try:
            if question_type == SurveyQuestionTypes.TEXT.value:
                data = copy.deepcopy(schema)
                TextOnlyFieldAnswerSchema(**data)
            elif question_type ==  SurveyQuestionTypes.MULTIPLE_CHOICE.value:
                data = copy.deepcopy(schema)
                MultipleChoiceFieldAnswerSchema(**data)
            else:
                raise ValidationError(_("Invalid question type"))
        except Exception as e:
            raise ValidationError(_("Invalid answer schema for the specified question type"))