from rest_framework import serializers

from authentication.serializers import TherapisyMinifiedReadSerializer
from rest_framework.validators import UniqueTogetherValidator
from surveys.enums import SurveyQuestionTypes
from surveys.models import TherapistSurvey, TherapistSurveyQuestion
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
            fields = ['id', 'index', 'ready_to_publish', 'active', 'description', 'question_type']
            model = TherapistSurveyQuestion


class SurveyMCQQuestionSchemaSerializer(serializers.Serializer):
    options = serializers.ListField(child=serializers.CharField())
    allow_multiple = serializers.BooleanField(default=False)

class TherapistSurveyQuestionMCQCreateSerializer(serializers.ModelSerializer):
    schema = SurveyMCQQuestionSchemaSerializer()

    class Meta:
        fields = ['description', 'survey', 'schema', 'image']
        model = TherapistSurveyQuestion

    def create(self, validated_data):
        validated_data['index'] = validated_data['survey'].questions.aggregate(max_idx=Max('index'))['max_idx'] + 1
        validated_data['question_type'] = SurveyQuestionTypes.MULTIPLE_CHOICE.value
        
        return super().create(validated_data)
    
class TherapistSurveyMCQUpdateSerializer(TherapistSurveyQuestionMCQCreateSerializer):

    class Meta:
        fields = ['description', 'schema', 'image']
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
        fields = ['description', 'survey', 'schema', 'image']
        model = TherapistSurveyQuestion

    def create(self, validated_data):
        validated_data['index'] = validated_data['survey'].questions.aggregate(max_idx=Max('index'))['max_idx'] + 1
        validated_data['question_type'] = SurveyQuestionTypes.TEXT.value
        
        return super().create(validated_data)
    
class TherapistSurveyTextUpdateSerializer(TherapistSurveyQuestionTextCreateSerializer):
    
        class Meta:
            fields = ['description', 'schema', 'image']
            model = TherapistSurveyQuestion
    
        def update(self, instance, validated_data):
            return super().update(instance, validated_data)

# ------------- therapist surveys

class TherapistSurveyFullReadSerializer(serializers.ModelSerializer):

    questions = serializers.SerializerMethodField()
    therapist = serializers.SerializerMethodField()

    def get_questions(self, instance: TherapistSurvey):
        return TherapistSurveyQuestionMiniReadSerializer(instance.questions.all().order_by('index'), many=True).data

    def get_therapist(self, instance: TherapistSurvey):
        return TherapisyMinifiedReadSerializer(instance.therapist.user).data

    class Meta:
        fields = [*[f.name for f in TherapistSurvey._meta.fields], 'questions']
        model = TherapistSurvey
        


class TherapistSurveyMiniReadSerializer(serializers.ModelSerializer):

    therapist = serializers.SerializerMethodField()

    def get_therapist(self, instance: TherapistSurvey):
        return TherapisyMinifiedReadSerializer(instance.therapist.user).data
    class Meta:
        fields = '__all__'
        model = TherapistSurvey

class TherapistSurveyWriteSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ['name', 'image']
        model = TherapistSurvey

        

    def create(self, validated_data):

        validated_data['therapist'] = self.context['request'].user.therapist_profile

        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        validated_data['therapist'] = self.context['request'].user.therapist_profile
        return super().update(instance, validated_data)