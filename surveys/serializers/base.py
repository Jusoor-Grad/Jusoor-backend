from numpy import require
from rest_framework import serializers

from authentication.serializers import PatientReadSerializer, TherapistMinifiedReadSerializer
from rest_framework.validators import UniqueTogetherValidator
from surveys.enums import PENDING, SurveyQuestionTypes
from surveys.models import TherapistSurvey, TherapistSurveyQuestion, TherapistSurveyQuestionResponse, TherapistSurveyResponse
from django.db.models import Max
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

# ------------- therapist survey questions

class TherapistSurveyQuestionFullReadSerializer(serializers.ModelSerializer):

    class Meta:
        fields ='__all__'
        model = TherapistSurveyQuestion


class TherapistSurveyQuestionMiniReadSerializer(serializers.ModelSerializer):
    
        class Meta:
            fields = ['id', 'index', 'active', 'description', 'question_type']
            model = TherapistSurveyQuestion


class SurveyMCQQuestionSchemaSerializer(serializers.Serializer):
    options = serializers.ListField(child=serializers.CharField())
    allow_multiple = serializers.BooleanField(default=False)

class TherapistSurveyQuestionMCQCreateSerializer(serializers.ModelSerializer):
    schema = SurveyMCQQuestionSchemaSerializer()

    class Meta:
        fields = ['description', 'survey', 'schema']
        model = TherapistSurveyQuestion

    def create(self, validated_data):
        validated_data['question_type'] = SurveyQuestionTypes.MULTIPLE_CHOICE.value
        
        return super().create(validated_data)
    
class TherapistSurveyMCQUpdateSerializer(TherapistSurveyQuestionMCQCreateSerializer):

    class Meta:
        fields = ['description', 'schema']
        model = TherapistSurveyQuestion

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    
class SurveyTextQuestionSchemaSerializer(serializers.Serializer):
    max_length = serializers.IntegerField(default=300)
    min_length = serializers.IntegerField(default=10)

    def validate(self, attrs):

        if attrs['max_length'] <= attrs['min_length']:
            raise ValidationError(_('Max length must be greater than min length'))

        return attrs

class TherapistSurveyQuestionTextCreateSerializer(serializers.ModelSerializer):
    schema = SurveyTextQuestionSchemaSerializer()

    class Meta:
        fields = ['description', 'survey', 'schema']
        model = TherapistSurveyQuestion

    def create(self, validated_data):
        validated_data['question_type'] = SurveyQuestionTypes.TEXT.value
        
        return super().create(validated_data)
    
class TherapistSurveyTextUpdateSerializer(TherapistSurveyQuestionTextCreateSerializer):
    
        class Meta:
            fields = ['description', 'schema']
            model = TherapistSurveyQuestion
    
        def update(self, instance, validated_data):
            return super().update(instance, validated_data)


class TherapistSurveyQuestionImageUploadSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ['image']
        model = TherapistSurveyQuestion


# ------------- therapist surveys

class TherapistSurveyFullReadSerializer(serializers.ModelSerializer):

    questions = serializers.SerializerMethodField()
    therapist = serializers.SerializerMethodField()

    def get_questions(self, instance: TherapistSurvey):
        return TherapistSurveyQuestionMiniReadSerializer(instance.questions.all().order_by('index'), many=True).data

    def get_therapist(self, instance: TherapistSurvey):
        return TherapistMinifiedReadSerializer(instance.created_by.user).data

    class Meta:
        fields = '__all__'
        model = TherapistSurvey
        


class TherapistSurveyMiniReadSerializer(serializers.ModelSerializer):

    therapist = serializers.SerializerMethodField()

    def get_therapist(self, instance: TherapistSurvey):
        return TherapistMinifiedReadSerializer(instance.created_by.user_profile).data
    class Meta:
        fields = '__all__'
        model = TherapistSurvey

class TherapistSurveyWriteSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ['name', 'image']
        model = TherapistSurvey     

    def create(self, validated_data):

        validated_data['created_by'] = self.context['request'].user.therapist_profile

        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        validated_data['last_updated_by'] = self.context['request'].user.therapist_profile
        return super().update(instance, validated_data)
    
#  ----------------- survey responses
    
class TherapistSurveyQuestionResponseFullReadSerializer(serializers.ModelSerializer):

    index = serializers.SerializerMethodField()
    question = TherapistSurveyQuestionFullReadSerializer()

    def get_index(self, instance: TherapistSurveyQuestionResponse):
        return instance.question.index
    
    class Meta:
        fields = ['id', 'answer', 'survey', 'index', 'question']
        model = TherapistSurveyQuestionResponse


class ThreapistSurveyResponseMiniReadSerializer(serializers.ModelSerializer):

    patient = serializers.SerializerMethodField()

    def get_patient(self, instance: TherapistSurveyResponse):
        return PatientReadSerializer(instance.patient.user).data

    class Meta:
        fields = '__all__'
        model = TherapistSurveyResponse    

class ThreapistSurveyResponseFullReadSerializer(ThreapistSurveyResponseMiniReadSerializer):

    answers = serializers.SerializerMethodField()

    def get_answers(self, instance: TherapistSurveyResponse):
        return TherapistSurveyQuestionResponseFullReadSerializer(instance.response_answers.all().order_by('question__index'), many=True).data

    class Meta:
        fields = '__all__'
        model = TherapistSurveyResponse

class TherapistSurveyResponseCreateSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ['survey']
        model = TherapistSurveyResponse

    def create(self, validated_data):

        validated_data['patient'] = self.context['request'].user.patient_profile
        validated_data['status'] = 'PENDING'

        return super().create(validated_data)

class TherapistSurveyQuestionAnswerSerializer(serializers.Serializer):
    question = serializers.PrimaryKeyRelatedField(queryset=TherapistSurveyQuestion.objects.all())
    survey = serializers.PrimaryKeyRelatedField(queryset=TherapistSurvey.objects.all())

    
    def create(self, validated_data):
        # if we haven't created the survey response, we create it
        survey_response, _ = TherapistSurveyResponse.objects.get_or_create(
            survey=validated_data['survey'], patient=self.context['request'].user.patient_profile, status=PENDING).last()

        validated_data['survey_response'] = survey_response
        # if the parent responsedidn't include this question, we create it. Else, we update it
        TherapistSurveyQuestionResponse.objects.update_or_create(**validated_data)

        return validated_data
    
class TherapistSurveyQuestionMCQResponseSerializer(TherapistSurveyQuestionAnswerSerializer):

    answer = serializers.ListField(child=serializers.IntegerField(), required=True)
    def validate_answers(self, value):

        if len(value) != len(set(value)):
            raise ValidationError(_('Answers must be unique'))
        if len(value) < 1:
            raise ValidationError(_('Must have at least 1 answer'))


    def validate(self, attrs):

        answers = attrs['answers']
        
        if len(answers) > 1 and not attrs['allow_multiple']:
            raise ValidationError(_('Multiple answers are not allowed'))

        if attrs['question'].question_type != SurveyQuestionTypes.MULTIPLE_CHOICE:
            raise ValidationError(_('Question is not of type multiple choice'))

        if not attrs['survey'].questions.filter(id=attrs['question'].id).exists():
            raise ValidationError(_('Question does not belong to the targeted survey'))

        return attrs

class TherapistSurveyQuestionTextResponseSerializer(TherapistSurveyQuestionAnswerSerializer):

    answer = serializers.CharField(required=True)

    def validate(self, attrs):

        if attrs['question'].question_type != SurveyQuestionTypes.TEXT:
            raise ValidationError(_('Question is not of type text'))

        if not attrs['survey'].questions.filter(id=attrs['question'].id).exists():
            raise ValidationError(_('Question does not belong to the targeted survey'))

        return attrs