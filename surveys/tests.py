from django.test import TestCase, tag
from datetime import datetime
from django.utils import timezone
from faker import Faker
from core.mock import PatientMock, TherapistMock
from core.models import Therapist
from core.utils.testing import auth_request
from rest_framework.test import APIRequestFactory
from surveys.enums import COMPLETED, PENDING, SurveyQuestionTypes
from surveys.mock import TherapistSurveyMocker
from surveys.models import TherapistSurvey, TherapistSurveyQuestion, TherapistSurveyQuestionResponse, TherapistSurveyResponse
from surveys.views import TherapistSurveyQuestionViewset, TherapistSurveyResponseViewset, TherapistSurveyViewset
from django.core.files.uploadedfile import SimpleUploadedFile
# Create your tests here.

class TherapistSurveyTherapistTestCase(TestCase):
    
    def setUp(self):
        viewset = TherapistSurveyViewset
        self.list = viewset.as_view({'get': 'list'})
        self.retrieve = viewset.as_view({'get': 'retrieve'})
        self.create = viewset.as_view({'post': 'create'})
        self.update = viewset.as_view({'put': 'update'})
        self.delete = viewset.as_view({'delete': 'destroy'})
        self.partial_update = viewset.as_view({'patch': 'partial_update'})
        self.publish = viewset.as_view({'patch': 'publish'})
        self.hide = viewset.as_view({'patch': 'hide'})
        self.factory = APIRequestFactory()

    @tag('test-list-surveys')
    def test_list(self):
        
        surveys = TherapistSurveyMocker.mock_instances(3, 5)
        patient = PatientMock.mock_instances(1)[0]
        request = auth_request(self.factory.get, 'surveys/', user=patient.user)
        response = self.list(request)

        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 3)

    @tag('test-retrieve-survey')
    def test_retrieve(self):
        
        survey = TherapistSurveyMocker.mock_instances(1, question_n=3)[0]
        patient = PatientMock.mock_instances(1)[0]
        request = auth_request(self.factory.get, 'surveys/', user=patient.user)
        response = self.retrieve(request, pk=survey.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], survey.id)

    @tag('test-create-survey-success')
    def test_create_success(self):

        faker = Faker()
        image: bytes = faker.image()
        data = {
            'image': SimpleUploadedFile(name='test_image.png', content=image, content_type='image/png'),
            'name': faker.name(),
            'description': faker.text(),
        }
        user = TherapistMock.mock_instances(1)[0].user
        request = auth_request(self.factory.post, 'surveys/', body=data, format='multipart', user=user)
        response = self.create(request)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(TherapistSurvey.objects.all()), 1)

    @tag('test-create-survey-failure-perm')
    def test_create_failure_perm(self):

        faker = Faker()
        image: bytes = faker.image()
        data = {
            'image': SimpleUploadedFile(name='test_image.png', content=image, content_type='image/png'),
            'name': faker.name(),
            'description': faker.text(),
        }
        user = PatientMock.mock_instances(1)[0].user
        request = auth_request(self.factory.post, 'surveys/', body=data, format='multipart', user=user)
        response = self.create(request)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(len(TherapistSurvey.objects.all()), 0)

    @tag('test-create-survey-fail-missing-fields')
    def test_create_failure_missing_fields(self):
        
        data = {}
        user = TherapistMock.mock_instances(1)[0].user
        request = auth_request(self.factory.post, 'surveys/', body=data, format='json', user=user)
        response = self.create(request)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(TherapistSurvey.objects.all()), 0)

    @tag('test-update-survey-success')
    def test_update_success(self):

        survey = TherapistSurveyMocker.mock_instances(1)[0]
        faker = Faker()
        data = {
            'name': faker.name(),
            'description': faker.text(),
        }
        user = survey.created_by.user
        request = auth_request(self.factory.put, 'surveys/', body=data, format='json', user=user)
        response = self.update(request, pk=survey.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(TherapistSurvey.objects.get(pk=survey.id).name, data['name'])

    @tag('test-update-survey-failure-perm')
    def test_update_failure_perm(self):

        survey = TherapistSurveyMocker.mock_instances(1)[0]
        faker = Faker()
        data = {
            'name': faker.name(),
            'description': faker.text(),
        }
        user = PatientMock.mock_instances(1)[0].user
        request = auth_request(self.factory.put, 'surveys/', body=data, format='json', user=user)
        response = self.update(request, pk=survey.id)

        self.assertEqual(response.status_code, 403)
        self.assertNotEqual(TherapistSurvey.objects.get(pk=survey.id).name, data['name'])

    @tag('test-update-survey-failure-missing-fields')
    def test_update_failure_missing_fields(self):

        survey = TherapistSurveyMocker.mock_instances(1)[0]
        data = {}
        user = survey.created_by.user
        request = auth_request(self.factory.put, 'surveys/', body=data, format='json', user=user)
        response = self.update(request, pk=survey.id)

        self.assertEqual(response.status_code, 400)

    @tag('test-delete-survey-success')
    def test_delete_success(self):

        survey = TherapistSurveyMocker.mock_instances(1)[0]
        user = survey.created_by.user
        request = auth_request(self.factory.delete, 'surveys/', user=user)
        response = self.delete(request, pk=survey.id)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(len(TherapistSurvey.objects.all()), 0)

    @tag('test-delete-survey-failure-perm')
    def test_delete_failure_perm(self):

        survey = TherapistSurveyMocker.mock_instances(1)[0]
        user = PatientMock.mock_instances(1)[0].user
        request = auth_request(self.factory.delete, 'surveys/', user=user)
        response = self.delete(request, pk=survey.id)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(len(TherapistSurvey.objects.all()), 1)

    @tag('test-publish-survey-success')
    def test_publish_success(self):

        survey = TherapistSurveyMocker.mock_instances(1, question_n=4, survey_fixed_args={
            'active': False
        }, question_fixed_args={
            'active': True
        })[0]
        user = survey.created_by.user
        request = auth_request(self.factory.patch, f'surveys/{survey.id}/publish/', user=user)
        response = self.publish(request, pk=survey.id)

        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(TherapistSurvey.objects.get(pk=survey.id).active)

    @tag('test-publish-survey-failure-perm')
    def test_publish_failure_perm(self):

        survey = TherapistSurveyMocker.mock_instances(1, survey_fixed_args={
            'active': False
        })[0]
        user = PatientMock.mock_instances(1)[0].user
        request = auth_request(self.factory.patch, 'surveys/', user=user)
        response = self.publish(request, pk=survey.id)

        self.assertEqual(response.status_code, 403)
        self.assertFalse(TherapistSurvey.objects.get(pk=survey.id).active)

    @tag('test-publish-survey-failure-already-active')
    def test_publish_failure_already_active(self):

        survey = TherapistSurveyMocker.mock_instances(1, survey_fixed_args={
            'active': True
        })[0]
        user = survey.created_by.user
        request = auth_request(self.factory.patch, 'surveys/', user=user)
        response = self.publish(request, pk=survey.id)

        self.assertEqual(response.status_code, 400)
        self.assertTrue(TherapistSurvey.objects.get(pk=survey.id).active)

    @tag('test-hide-survey-success')
    def test_hide_success(self):

        survey = TherapistSurveyMocker.mock_instances(1, survey_fixed_args={
            'active': True
        })[0]
        user = survey.created_by.user
        request = auth_request(self.factory.patch, f'surveys/{survey.id}/hide/', user=user)
        response = self.hide(request, pk=survey.id)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(TherapistSurvey.objects.get(pk=survey.id).active)

    @tag('test-hide-survey-failure-perm')
    def test_hide_failure_perm(self):

        survey = TherapistSurveyMocker.mock_instances(1, survey_fixed_args={
            'active': True
        })[0]
        user = PatientMock.mock_instances(1)[0].user
        request = auth_request(self.factory.patch, f'surveys/{survey.id}/hide/', user=user)
        response = self.hide(request, pk=survey.id)

        self.assertEqual(response.status_code, 403)
        self.assertTrue(TherapistSurvey.objects.get(pk=survey.id).active)

    @tag('test-hide-survey-failure-already-inactive')
    def test_hide_failure_already_inactive(self):

        survey = TherapistSurveyMocker.mock_instances(1, survey_fixed_args={
            'active': False
        })[0]
        user = survey.created_by.user
        request = auth_request(self.factory.patch, 'surveys/{survey.id}/hide/', user=user)
        response = self.hide(request, pk=survey.id)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(TherapistSurvey.objects.get(pk=survey.id).active)

class TherapistSurveyQuestionTestCase(TestCase):
    
    def setUp(self):
        viewset = TherapistSurveyQuestionViewset
        self.list = viewset.as_view({'get': 'list'})
        self.retrieve_mc = viewset.as_view({'get': 'retrieve_mc_question'})
        self.retrieve_text = viewset.as_view({'get': 'retrieve_text_question'})
        self.create_mc = viewset.as_view({'post': 'create_mc_question'})
        self.create_text = viewset.as_view({'post': 'create_text_question'})
        self.update_mc = viewset.as_view({'put': 'update_mc_question'})
        self.update_text = viewset.as_view({'put': 'update_text_question'})
        self.delete = viewset.as_view({'delete': 'destroy'})
        self.upload_image = viewset.as_view({'post': 'upload_image'})
        self.publish = viewset.as_view({'patch': 'publish'})
        self.hide = viewset.as_view({'patch': 'hide'})
        self.factory = APIRequestFactory()

    @tag('test-list-questions')
    def test_list(self):
        
        survey = TherapistSurveyMocker.mock_instances(1, question_n=3)[0]
        patient = PatientMock.mock_instances(1)[0]
        request = auth_request(self.factory.get, 'survey-questions/', user=patient.user)
        response = self.list(request, survey_id=survey.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 3)

    @tag('test-retrieve-mc-question-success')
    def test_retrieve_mc(self):
        
        survey = TherapistSurveyMocker.mock_instances(1, question_n=3, question_fixed_args={
            'question_type': SurveyQuestionTypes.MULTIPLE_CHOICE.value
        })[0]
        question = survey.questions.filter(question_type=SurveyQuestionTypes.MULTIPLE_CHOICE.value).first()
        patient = PatientMock.mock_instances(1)[0]
        request = auth_request(self.factory.get, f'survey-questions/{question.id}/mcq/', user=patient.user)
        response = self.retrieve_mc(request, survey_id=survey.id, pk=question.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], question.id)

    @tag('test-retrieve-mc-question-incorrect-type')
    def test_retrieve_mc_incorrect_type(self):
        
        survey = TherapistSurveyMocker.mock_instances(1, question_n=3, question_fixed_args={
            'question_type': SurveyQuestionTypes.TEXT.value
        })[0]
        question = survey.questions.filter(question_type=SurveyQuestionTypes.TEXT.value).first()
        patient = PatientMock.mock_instances(1)[0]
        request = auth_request(self.factory.get, f'survey-questions/{question.id}/mcq/', user=patient.user)
        response = self.retrieve_mc(request, survey_id=survey.id, pk=question.id)

        self.assertEqual(response.status_code, 404)

    @tag('test-retrieve-text-question-success')
    def test_retrieve_text(self):
        
        survey = TherapistSurveyMocker.mock_instances(1, question_n=3, question_fixed_args={
            'question_type': SurveyQuestionTypes.TEXT.value
        })[0]
        question = survey.questions.filter(question_type=SurveyQuestionTypes.TEXT.value).first()
        patient = PatientMock.mock_instances(1)[0]
        request = auth_request(self.factory.get, f'survey-questions/{question.id}/text/', user=patient.user)
        response = self.retrieve_text(request, survey_id=survey.id, pk=question.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['id'], question.id)

    @tag('test-retrieve-text-question-incorrect-type')
    def test_retrieve_text_incorrect_type(self):
        
        survey = TherapistSurveyMocker.mock_instances(1, question_n=3, question_fixed_args={
            'question_type': SurveyQuestionTypes.MULTIPLE_CHOICE.value
        })[0]
        question = survey.questions.filter(question_type=SurveyQuestionTypes.MULTIPLE_CHOICE.value).first()
        patient = PatientMock.mock_instances(1)[0]
        request = auth_request(self.factory.get, f'survey-questions/{question.id}/text/', user=patient.user)
        response = self.retrieve_text(request, survey_id=survey.id, pk=question.id)

        self.assertEqual(response.status_code, 404)

    @tag('test-create-mc-question-success')
    def test_create_mc_success(self):
        
        survey = TherapistSurveyMocker.mock_instances(1, 0)[0]
        faker = Faker()
        data = {
            'description': faker.text(),
            'survey': survey.id,
            'schema': {'options': [faker.text() for _ in range(4)], 'allow_multiple': False}
        }
        user = survey.created_by.user
        request = auth_request(self.factory.post, 'survey-questions/mcq/', body=data, format='json', user=user)
        response = self.create_mc(request)

        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(survey.questions.all()), 1)

    @tag('test-create-mc-question-failure-perm')
    def test_create_mc_failure_perm(self):
        
        survey = TherapistSurveyMocker.mock_instances(1, 0)[0]
        faker = Faker()
        data = {
            'description': faker.text(),
            'survey': survey.id,
            'schema': {'options': [faker.text() for _ in range(4)], 'allow_multiple': False}
        }
        user = PatientMock.mock_instances(1)[0].user
        request = auth_request(self.factory.post, 'survey-questions/mcq/', body=data, format='json', user=user)
        response = self.create_mc(request)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(len(survey.questions.all()), 0)

    @tag('test-create-mc-question-failure-wrong-schema')
    def test_create_mc_failure_wrong_schema(self):
        
        survey = TherapistSurveyMocker.mock_instances(1, 0)[0]
        faker = Faker()
        data = {
            'description': faker.text(),
            'survey': survey.id,
            'schema': {'min_length': 10, 'max_length': 300}
        }
        user = survey.created_by.user
        request = auth_request(self.factory.post, 'survey-questions/mcq/', body=data, format='json', user=user)
        response = self.create_mc(request)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(survey.questions.all()), 0)

    @tag('test-create-text-question-success')
    def test_create_text_success(self):
        
        survey = TherapistSurveyMocker.mock_instances(1, 0)[0]
        faker = Faker()
        data = {
            'description': faker.text(),
            'survey': survey.id,
            'schema': {'min_length': 10, 'max_length': 300}
        }
        user = survey.created_by.user
        request = auth_request(self.factory.post, 'survey-questions/text/', body=data, format='json', user=user)
        response = self.create_text(request)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(survey.questions.all()), 1)

    @tag('test-create-text-question-failure-perm')
    def test_create_text_failure_perm(self):
        
        survey = TherapistSurveyMocker.mock_instances(1, 0)[0]
        faker = Faker()
        data = {
            'description': faker.text(),
            'survey': survey.id,
            'schema': {'min_length': 10, 'max_length': 300}
        }
        user = PatientMock.mock_instances(1)[0].user
        request = auth_request(self.factory.post, 'survey-questions/text/', body=data, format='json', user=user)
        response = self.create_text(request)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(len(survey.questions.all()), 0)

    @tag('update-mc-question-success')
    def test_update_mc_success(self):
        
        survey = TherapistSurveyMocker.mock_instances(1, question_n=1, question_fixed_args={
            'question_type': SurveyQuestionTypes.MULTIPLE_CHOICE.value
        })[0]
        question = survey.questions.first()
        faker = Faker()
        data = {
            'description': faker.text(),
            'schema': {'options': [faker.text() for _ in range(4)], 'allow_multiple': False}
        }
        user = survey.created_by.user
        request = auth_request(self.factory.put, f'survey-questions/{question.id}/mcq/', body=data, format='json', user=user)
        response = self.update_mc(request, pk=question.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(TherapistSurvey.objects.get(pk=survey.id).questions.first().description, data['description'])

    @tag('update-mc-question-failure-perm')
    def test_update_mc_failure_perm(self):
        
        survey = TherapistSurveyMocker.mock_instances(1, question_n=1, question_fixed_args={
            'question_type': SurveyQuestionTypes.MULTIPLE_CHOICE.value
        })[0]
        question = survey.questions.first()
        faker = Faker()
        data = {
            'description': faker.text(),
            'schema': {'options': [faker.text() for _ in range(4)], 'allow_multiple': False}
        }
        user = PatientMock.mock_instances(1)[0].user
        request = auth_request(self.factory.put, f'survey-questions/{question.id}/mcq/', body=data, format='json', user=user)
        response = self.update_mc(request, survey_id=survey.id, pk=question.id)

        self.assertEqual(response.status_code, 403)
        self.assertNotEqual(TherapistSurvey.objects.get(pk=survey.id).questions.first().description, data['description'])

    @tag('update-mc-question-failure-wrong-schema')
    def test_update_mc_failure_wrong_schema(self):
        
        survey = TherapistSurveyMocker.mock_instances(1, question_n=1, question_fixed_args={
            'question_type': SurveyQuestionTypes.MULTIPLE_CHOICE.value
        })[0]
        question = survey.questions.first()
        faker = Faker()
        data = {
            'description': faker.text(),
            'schema': {'min_length': 10, 'max_length': 300}
        }
        user = survey.created_by.user
        request = auth_request(self.factory.put, f'survey-questions/{question.id}/mcq/', body=data, format='json', user=user)
        response = self.update_mc(request, survey_id=survey.id, pk=question.id)

        self.assertEqual(response.status_code, 400)
        self.assertNotEqual(TherapistSurvey.objects.get(pk=survey.id).questions.first().description, data['description'])

    @tag('update-text-question-success')
    def test_update_text_success(self):
        
        survey = TherapistSurveyMocker.mock_instances(1, question_n=1, question_fixed_args={
            'question_type': SurveyQuestionTypes.TEXT.value
        })[0]
        question = survey.questions.first()
        faker = Faker()
        data = {
            'description': faker.text(),
            'schema': {'min_length': 10, 'max_length': 300}
        }
        user = survey.created_by.user
        request = auth_request(self.factory.put, f'survey-questions/{question.id}/text/', body=data, format='json', user=user)
        response = self.update_text(request, survey_id=survey.id, pk=question.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(TherapistSurvey.objects.get(pk=survey.id).questions.first().description, data['description'])

    @tag('update-text-question-failure-perm')
    def test_update_text_failure_perm(self):
        
        survey = TherapistSurveyMocker.mock_instances(1, question_n=1, question_fixed_args={
            'question_type': SurveyQuestionTypes.TEXT.value
        })[0]
        question = survey.questions.first()
        faker = Faker()
        data = {
            'description': faker.text(),
            'schema': {'min_length': 10, 'max_length': 300}
        }
        user = PatientMock.mock_instances(1)[0].user
        request = auth_request(self.factory.put, f'survey-questions/{question.id}/text/', body=data, format='json', user=user)
        response = self.update_text(request, survey_id=survey.id, pk=question.id)

        self.assertEqual(response.status_code, 403)
        self.assertNotEqual(TherapistSurvey.objects.get(pk=survey.id).questions.first().description, data['description'])

    @tag('question-image-upload-success')
    def test_upload_image_success(self):
        
        survey = TherapistSurveyMocker.mock_instances(1, question_n=1)[0]
        question = survey.questions.first()
        faker = Faker()
        image: bytes = faker.image()
        data = {
            'image': SimpleUploadedFile(name='test_image.png', content=image, content_type='image/png')
        }
        user = survey.created_by.user
        request = auth_request(self.factory.post, f'survey-questions/{question.id}/upload-image/', body=data, format='multipart', user=user)
        response = self.upload_image(request, survey_id=survey.id, pk=question.id)

        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(TherapistSurvey.objects.get(pk=survey.id).questions.first().image)

    @tag('question-image-upload-failure-perm')
    def test_upload_image_failure_perm(self):
        
        survey = TherapistSurveyMocker.mock_instances(1, question_n=1)[0]
        question = survey.questions.first()
        faker = Faker()
        image: bytes = faker.image()
        data = {
            'image': SimpleUploadedFile(name='test_image.png', content=image, content_type='image/png')
        }
        user = PatientMock.mock_instances(1)[0].user
        request = auth_request(self.factory.post, f'survey-questions/{question.id}/upload-image/', body=data, format='multipart', user=user)
        response = self.upload_image(request, survey_id=survey.id, pk=question.id)
        
        self.assertEqual(response.status_code, 403)
        self.assertFalse(bool(TherapistSurvey.objects.get(pk=survey.id).questions.first().image))

    @tag('publish-question-success')
    def test_publish_success(self):
        
        survey = TherapistSurveyMocker.mock_instances(1, question_n=1, question_fixed_args={
            'active': False
        })[0]
        question = survey.questions.first()
        user = survey.created_by.user
        request = auth_request(self.factory.patch, f'survey-questions/{question.id}/publish/', user=user)
        response = self.publish(request, survey_id=survey.id, pk=question.id)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(TherapistSurveyQuestion.objects.get(pk=question.id).active)

    @tag('publish-question-failure-perm')
    def test_publish_failure_perm(self):
        
        survey = TherapistSurveyMocker.mock_instances(1, question_n=1, question_fixed_args={
            'active': False
        })[0]
        question = survey.questions.first()
        user = PatientMock.mock_instances(1)[0].user
        request = auth_request(self.factory.patch, f'survey-questions/{question.id}/publish/', user=user)
        response = self.publish(request, survey_id=survey.id, pk=question.id)

        self.assertEqual(response.status_code, 403)
        self.assertFalse(TherapistSurvey.objects.get(pk=survey.id).questions.first().active)

    @tag('publish-question-failure-already-active')
    def test_publish_failure_already_active(self):
        
        survey = TherapistSurveyMocker.mock_instances(1, question_n=1, question_fixed_args={
            'active': True
        })[0]
        question = survey.questions.first()
        user = survey.created_by.user
        request = auth_request(self.factory.patch, f'survey-questions/{question.id}/publish/', user=user)
        response = self.publish(request, survey_id=survey.id, pk=question.id)

        self.assertEqual(response.status_code, 400)
        self.assertTrue(TherapistSurvey.objects.get(pk=survey.id).questions.first().active)

    @tag('hide-question-success')
    def test_hide_success(self):
        
        survey = TherapistSurveyMocker.mock_instances(1, question_n=1, question_fixed_args={
            'active': True
        })[0]
        question = survey.questions.first()
        user = survey.created_by.user
        request = auth_request(self.factory.patch, f'survey-questions/{question.id}/hide/', user=user)
        response = self.hide(request, survey_id=survey.id, pk=question.id)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(TherapistSurvey.objects.get(pk=survey.id).questions.first().active)

    @tag('hide-question-failure-perm')
    def test_hide_failure_perm(self):
        
        survey = TherapistSurveyMocker.mock_instances(1, question_n=1, question_fixed_args={
            'active': True
        })[0]
        question = survey.questions.first()
        user = PatientMock.mock_instances(1)[0].user
        request = auth_request(self.factory.patch, f'survey-questions/{question.id}/hide/', user=user)
        response = self.hide(request, survey_id=survey.id, pk=question.id)

        self.assertEqual(response.status_code, 403)
        self.assertTrue(TherapistSurvey.objects.get(pk=survey.id).questions.first().active)

    @tag('hide-question-failure-already-inactive')
    def test_hide_failure_already_inactive(self):
        
        survey = TherapistSurveyMocker.mock_instances(1, question_n=1, question_fixed_args={
            'active': False
        })[0]
        question = survey.questions.first()
        user = survey.created_by.user
        request = auth_request(self.factory.patch, f'survey-questions/{question.id}/hide/', user=user)
        response = self.hide(request, survey_id=survey.id, pk=question.id)

        self.assertEqual(response.status_code, 400)
        self.assertFalse(TherapistSurvey.objects.get(pk=survey.id).questions.first().active)

class TherapistSurveyResponseTestCase(TestCase):

    def setUp(self):
        viewset = TherapistSurveyResponseViewset
        self.list = viewset.as_view({'get': 'list'})
        self.retrieve = viewset.as_view({'get': 'retrieve'})
        self.create = viewset.as_view({'post': 'create'})
        self.answer_mc_question = viewset.as_view({'post': 'answer_mc_question'})
        self.answer_text_question = viewset.as_view({'post': 'answer_text_question'})
        self.submit = viewset.as_view({'put': 'submit'})

        self.factory = APIRequestFactory()

    @tag('list-responses-success')
    def test_list(self):
        
        survey = TherapistSurveyMocker.mock_instances(3, question_n=3, include_responses=True)[0]
        patient = TherapistMock.mock_instances(1)[0]
        request = auth_request(self.factory.get, 'survey-responses/', user=patient.user)
        response = self.list(request, survey_id=survey.id)


        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 3)

    @tag('retrieve-response-success')
    def test_retrieve(self):
        
        survey = TherapistSurveyMocker.mock_instances(1, question_n=5, include_responses=True)[0]
        response = survey.responses.first()
        patient = TherapistMock.mock_instances(1)[0]
        request = auth_request(self.factory.get, f'survey-responses/{response.id}/', user=patient.user)
        response = self.retrieve(request, survey_id=survey.id, pk=response.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['answers']), 5)

    @tag('create-response-success')
    def test_create_success(self):
        
        survey = TherapistSurveyMocker.mock_instances(1, question_n=5, survey_fixed_args= {
            'active': True
        })[0]
        patient = PatientMock.mock_instances(1)[0]
        data = {
            'survey': survey.id
        }
        request = auth_request(self.factory.post, 'survey-responses/', body=data, user=patient.user)
        response = self.create(request, survey_id=survey.id)

        
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(survey.responses.all()), 1)

    @tag('create-response-failure-perm')
    def test_create_failure_perm(self):
        
        survey = TherapistSurveyMocker.mock_instances(1, question_n=5)[0]
        patient = TherapistMock.mock_instances(1)[0]
        data = {
            'survey': survey.id
        }
        request = auth_request(self.factory.post, 'survey-responses/', body=data, user=patient.user)
        response = self.create(request, survey_id=survey.id)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(len(survey.responses.all()), 0)

    @tag('create-response-failure-in-progress-exists')
    def test_create_failure_in_progress_exists(self):
        
        survey = TherapistSurveyMocker.mock_instances(1, question_n=5)[0]
        patient = PatientMock.mock_instances(1)[0]
        response = TherapistSurveyResponse.objects.create(
            survey=survey,
            patient=patient,
            status=PENDING
        )
        request = auth_request(self.factory.post, 'survey-responses/', user=patient.user)
        response = self.create(request, survey_id=survey.id)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(len(survey.responses.all()), 1)


    @tag('answer-mc-question-success')
    def test_answer_mc_success(self):
        
        survey = TherapistSurveyMocker.mock_instances(1, question_n=1, question_fixed_args={
            'question_type': SurveyQuestionTypes.MULTIPLE_CHOICE.value
        
        })[0]
        response = TherapistSurveyResponse.objects.create(
            survey=survey,
            patient=PatientMock.mock_instances(1)[0]
        )
        question = survey.questions.first()
        
        faker = Faker()
        answer =  [ faker.random.choice((range(len(question.schema['options'])))) ]
        data = {
            'answer': answer
        }
        request = auth_request(self.factory.post, f'survey-responses/mcq/{question.id}', body=data, user=response.patient.user)
        response = self.answer_mc_question(request, pk=response.id, question_id=question.id)

        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(TherapistSurveyQuestionResponse.objects.count(), 1)

    @tag('answer-mc-question-failure-perm')
    def test_answer_mc_failure_perm(self):
        
        survey = TherapistSurveyMocker.mock_instances(1, question_n=1, question_fixed_args={
            'question_type': SurveyQuestionTypes.MULTIPLE_CHOICE.value
        })[0]
        response = TherapistSurveyResponse.objects.create(
            survey=survey,
            patient=PatientMock.mock_instances(1)[0]
        )
        question = survey.questions.first()
        faker = Faker()
        answer =  [ faker.random.choice((range(len(question.schema['options'])))) ]
        data = {
            'answer': answer
        }
        request = auth_request(self.factory.post, f'survey-responses/mcq/{question.id}', body=data, user=TherapistMock.mock_instances(1)[0].user)
        response = self.answer_mc_question(request, pk=response.id, question_id=question.id)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(TherapistSurveyQuestionResponse.objects.count(), 0)

    @tag('answer-mc-question-failure-incorrect-schema')
    def test_answer_mc_failure_incorrect_schema(self):
        
        survey = TherapistSurveyMocker.mock_instances(1, question_n=1, question_fixed_args={
            'question_type': SurveyQuestionTypes.MULTIPLE_CHOICE.value
        })[0]
        response = TherapistSurveyResponse.objects.create(
            survey=survey,
            patient=PatientMock.mock_instances(1)[0]
        )
        question = survey.questions.first()
        
        answer =  "wrong answer"
        data = {
            'answer': answer
        }
        request = auth_request(self.factory.post, f'survey-responses/mcq/{question.id}', body=data, user=response.patient.user)
        response = self.answer_mc_question(request, pk=response.id, question_id=question.id)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(TherapistSurveyQuestionResponse.objects.count(), 0)

    @tag('answer-text-question-success')
    def test_answer_text_success(self):
        
        survey = TherapistSurveyMocker.mock_instances(1, question_n=1, question_fixed_args={
            'question_type': SurveyQuestionTypes.TEXT.value
        })[0]
        response = TherapistSurveyResponse.objects.create(
            survey=survey,
            patient=PatientMock.mock_instances(1)[0]
        )
        question = survey.questions.first()

        faker = Faker()
        answer = faker.text()
        data = {
            'answer': answer
        }
        request = auth_request(self.factory.post, f'survey-responses/text/{question.id}', body=data, user=response.patient.user)
        response = self.answer_text_question(request, pk=response.id, question_id=question.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(TherapistSurveyQuestionResponse.objects.count(), 1)  

    @tag('answer-text-question-failure-perm')
    def test_answer_text_failure_perm(self):
        
        survey = TherapistSurveyMocker.mock_instances(1, question_n=1, question_fixed_args={
            'question_type': SurveyQuestionTypes.TEXT.value
        })[0]
        response = TherapistSurveyResponse.objects.create(
            survey=survey,
            patient=PatientMock.mock_instances(1)[0]
        )
        question = survey.questions.first()
        faker = Faker()
        answer = faker.text()
        data = {
            'answer': answer
        }
        request = auth_request(self.factory.post, f'survey-responses/text/{question.id}', body=data, user=TherapistMock.mock_instances(1)[0].user)
        response = self.answer_text_question(request, pk=response.id, question_id=question.id)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(TherapistSurveyQuestionResponse.objects.count(), 0)

    @tag('answer-text-question-failure-incorrect-schema')
    def test_answer_text_failure_incorrect_schema(self):
        
        survey = TherapistSurveyMocker.mock_instances(1, question_n=1, question_fixed_args={
            'question_type': SurveyQuestionTypes.TEXT.value
        })[0]
        response = TherapistSurveyResponse.objects.create(
            survey=survey,
            patient=PatientMock.mock_instances(1)[0]
        )
        question = survey.questions.first()
        answer =  [ 1 ]
        data = {
            'answer': answer
        }
        request = auth_request(self.factory.post, f'survey-responses/text/{question.id}', body=data, user=response.patient.user)
        response = self.answer_text_question(request, pk=response.id, question_id=question.id)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(TherapistSurveyQuestionResponse.objects.count(), 0)


    @tag('submit-response-success')
    def test_submit_success(self):
        
        survey = TherapistSurveyMocker.mock_instances(1, question_n=5, include_responses=True)[0]
        survey_response = survey.responses.first()
        user = survey_response.patient.user
        request = auth_request(self.factory.put, f'survey-responses/{survey_response.id}/submit/', user=user)
        response = self.submit(request, pk=survey_response.id)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(TherapistSurveyResponse.objects.get(pk=survey_response.id).status, COMPLETED)

    @tag('submit-response-failure-perm')
    def test_submit_failure_perm(self):
        
        survey = TherapistSurveyMocker.mock_instances(1, question_n=5, include_responses=True)[0]
        survey_response = survey.responses.first()
        user = TherapistMock.mock_instances(1)[0].user
        request = auth_request(self.factory.put, f'survey-responses/{survey_response.id}/submit/', user=user)
        response = self.submit(request, pk=survey_response.id)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(TherapistSurveyResponse.objects.get(pk=survey_response.id).status, PENDING)

    @tag('submit-response-failure-already-completed')
    def test_submit_failure_already_completed(self):
        
        survey = TherapistSurveyMocker.mock_instances(1, question_n=5, include_responses=True, response_fixed_args= {
            'status': COMPLETED
        })[0]
        survey_response = survey.responses.first()
        
        user = survey_response.patient.user
        request = auth_request(self.factory.put, f'survey-responses/{survey_response.id}/submit/', user=user)
        response = self.submit(request, pk=survey_response.id)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(TherapistSurveyResponse.objects.get(pk=survey_response.id).status, COMPLETED)

    @tag('submit-response-failure-in-progress')
    def test_submit_failure_in_progress(self):
        
        survey = TherapistSurveyMocker.mock_instances(1, question_n=5, include_responses=False, question_fixed_args= {
            'question_type': SurveyQuestionTypes.TEXT.value
        })[0]
        survey_response = TherapistSurveyResponse.objects.create(
            survey=survey,
            patient=PatientMock.mock_instances(1)[0]
        )

        # creating only a single question resposne for the survey
        question = survey.questions.first()
        TherapistSurveyQuestionResponse.objects.create(
            survey_response=survey_response,
            survey=survey,
            question=question,
            answer="test"
        )


        user = survey_response.patient.user
        request = auth_request(self.factory.put, f'survey-responses/{survey_response.id}/submit/', user=user)
        response = self.submit(request, pk=survey_response.id)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(TherapistSurveyResponse.objects.get(pk=survey_response.id).status, PENDING)