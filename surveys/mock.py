


from tomlkit import boolean
from chat import mock
from core.mock import PatientMock, TherapistMock
from core.models import Therapist
from surveys.enums import SurveyQuestionTypes
from typing import Dict
from faker import Faker
from django.db import transaction

from surveys.models import TherapistSurvey, TherapistSurveyQuestion, TherapistSurveyQuestionResponse, TherapistSurveyResponse

fake = Faker()

class TherapistSurveyMocker():

    @staticmethod
    @transaction.atomic
    def mock_instances(survey_n: int = 2, question_n: int = 4, include_responses: bool = False, survey_fixed_args: Dict = None, question_fixed_args: Dict = None):
        """
        mocking N surveys with M questions each, while hving optionally fixed arguments
        for the creation of the survey as well as its arguments
        """
        
        # 1. create the surveys
        surveys = [ TherapistSurveyMocker.mock_survey(survey_fixed_args) for _ in range(survey_n) ]
        surveys= TherapistSurvey.objects.bulk_create(surveys)
        # 2. create the questions
        questions = []
        for survey in surveys:
            for i in range(question_n):
                questions.append(TherapistSurveyMocker.mock_question(survey, fake.random.choice([SurveyQuestionTypes.TEXT.value, SurveyQuestionTypes.MULTIPLE_CHOICE.value]),
                                                                     index=i,fixed_args=question_fixed_args))
        TherapistSurveyQuestion.objects.bulk_create(questions)

        # 3. create the responses
        if include_responses:
            for survey in surveys:
                TherapistSurveyMocker.mock_resposne(survey)

        return surveys

    @staticmethod
    def mock_survey(fixed_args: Dict = None):

        therapist: Therapist = TherapistMock.mock_instances(1)[0]
        
        body = {
            'created_by': therapist,
            'name': fake.name(),
            'description': fake.sentence(), # 'survey description
            'image': None,
            'active': False,
        }

        
        if fixed_args:
            body.update(fixed_args)

        return TherapistSurvey(**body)

    @staticmethod
    def mock_question( survey: TherapistSurvey, type: SurveyQuestionTypes,index: int, fixed_args: Dict):
        
        body = {
            'survey': survey,
            'description': fake.sentence(),
            'question_type': type,
            'schema': TherapistSurveyMocker.mock_q_schema(type),
            'active': False,
            'index': index
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
    def mock_resposne(survey: TherapistSurvey):
        
        response = TherapistSurveyResponse.objects.create(
            survey=survey,
            patient=PatientMock.mock_instances(1)[0],
        )

        responses = []
        for question in survey.questions.all():
            responses.append(TherapistSurveyMocker.mock_resposne_question(question, response))
        
        return TherapistSurveyQuestionResponse.objects.bulk_create(responses)

    @staticmethod
    def mock_resposne_question(question: TherapistSurveyQuestion, response: TherapistSurveyResponse):
        
        if question.question_type == SurveyQuestionTypes.MULTIPLE_CHOICE.value:
            answer= TherapistSurveyMocker.mock_mcq_answer(question)
        elif question.question_type == SurveyQuestionTypes.TEXT.value:
            answer=  TherapistSurveyMocker.mock_text_answer(question)
        else:
            raise ValueError('Invalid question type')
        
        return TherapistSurveyQuestionResponse(
            survey_response=response,
            survey=question.survey,
            question=question,
            answer=answer
        )

    @staticmethod
    def mock_mcq_answer(question: TherapistSurveyQuestion):
        
        return list(set(fake.random_int(0, len(question.schema['options']) - 1) for _ in range(fake.random_int(1, 3))))
        

    @staticmethod
    def mock_text_answer(question: TherapistSurveyQuestion):
        return fake.sentence()
        