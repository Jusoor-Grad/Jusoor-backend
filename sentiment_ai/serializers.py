from sentiment_ai.models import StudentPatientSentimentPosture
from rest_framework import serializers

class StudentPatientSentimentFullPostureReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentPatientSentimentPosture
        fields = '__all__'

class StudentPatientSentimentPostureMiniReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentPatientSentimentPosture
        fields = ['id', 'date', 'score']