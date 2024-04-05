
from enum import Enum
from django.utils.translation import gettext_lazy as _

class SurveyQuestionTypes(Enum):
    TEXT = 'text'
    MULTIPLE_CHOICE = 'multiple_choice'

SURVEY_QUESTION_TYPES: dict[SurveyQuestionTypes, str] = {
    SurveyQuestionTypes.TEXT.value: _("A question of type raw text"),
    SurveyQuestionTypes.MULTIPLE_CHOICE.value: _("A question of type: multiple choice")
}


CANCELLED = 'CANCELLED'
PENDING = 'PENDING'
COMPLETED = 'COMPLETED'
SURVEY_RESPONSE_STATUSES = {
    PENDING: _("The survey has not been completed yet"),
    CANCELLED: _('The response has been cancelled due to a cancelled appointment'),
    COMPLETED: _("The survey has been completed")
}
