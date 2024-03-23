


from tomlkit import boolean
from chat import mock
from core.models import Therapist
from surveys.enums import SurveyQuestionTypes
from typing import Dict
from faker import Faker

from surveys.models import TherapistSurvey, TherapistSurveyQuestion

fake = Faker()

class TherapistSurveyMocker():


    @staticmethod
    def mock_instances(survey_n: int, question_n: int, include_responses: bool = False, survey_fixed_args: Dict = None, question_fixed_args: Dict = None):
        """
        mocking N surveys with M questions each, while hving optionally fixed arguments
        for the creation of the survey as well as its arguments
        """
        
        # 1. create the surveys
        surveys = [ TherapistSurveyMocker.mock_survey(survey_fixed_args) for _ in range(survey_n) ]
        TherapistSurvey.objects.bulk_create(surveys)
        # 2. create the questions
        questions = []
        for survey in surveys:
            for _ in range(question_n):
                questions.append(TherapistSurveyMocker.mock_question(survey, fake.random.choice([SurveyQuestionTypes.TEXT.value, SurveyQuestionTypes.MULTIPLE_CHOICE.value]),question_fixed_args))
        TherapistSurveyQuestion.objects.bulk_create(questions)

    @staticmethod
    def mock_survey(fixed_args: Dict = None):
        
        body = {
            'therapist': Therapist.objects.order_by('?').first(),
            'name': fake.sentence(),
            'image': None,
            'active': False,
            'ready_to_publish': fake.boolean() 
        }

        
        if fixed_args:
            body.update(fixed_args)

        return TherapistSurvey(**body)

    @staticmethod
    def mock_question( survey: TherapistSurvey, type: SurveyQuestionTypes, fixed_args: Dict):
        
        body = {
            'survey': survey,
            'description': fake.sentence(),
            'question_type': type.value,
            'answer': TherapistSurveyMocker.mock_q_schema(type.value),
            'active': False,
            'ready_to_publish': fake.boolean()
        }
        
        
        if fixed_args:
            body.update(fixed_args)

        return TherapistSurveyQuestion(**body)
    
    @staticmethod
    def mock_q_schema(question_type: SurveyQuestionTypes):
        
        if question_type == SurveyQuestionTypes.MULTIPLE_CHOICE.value:
            return TherapistSurveyMocker.mock_mcq_schema()
        elif question_type == SurveyQuestionTypes.TEXT.value:
            return TherapistSurveyMocker.mock_text_q_schema()
        else:
            raise ValueError('Invalid question type')

    
    @staticmethod
    def mock_mcq_schema():
        return {
            'options': [fake.sentence() for _ in range(4)],
            'allow_multiple': fake.boolean()
        }
    
    @staticmethod
    def mock_text_q_schema():
        return {
            'max_length': fake.random_int(11, 300),
            'min_length': fake.random_int(1, 10)
        }
    
    @staticmethod
    def mock_resposne(question: TherapistSurveyQuestion, mcq_fixed_args: Dict = None, text_fixed_args: Dict = None):
        pass

    @staticmethod
    def mock_mcq_answer(question: TherapistSurveyQuestion, fixed_args: Dict = None):
        pass

    @staticmethod
    def mock_text_answer(question: TherapistSurveyQuestion, fixed_args: Dict = None):
        pass