

from sqlalchemy import desc
from core.serializers import HttpErrorResponseSerializer, HttpErrorSerializer, HttpPaginatedSerializer, HttpSuccessResponseSerializer
from surveys.serializers.base import SurveyMCQQuestionSchemaSerializer, SurveyTextQuestionSchemaSerializer, TherapistSurveyMCQUpdateSerializer, TherapistSurveyMiniReadSerializer, TherapistSurveyFullReadSerializer, TherapistSurveyQuestionFullReadSerializer, TherapistSurveyQuestionMCQCreateSerializer, TherapistSurveyQuestionMiniReadSerializer, TherapistSurveyQuestionTextCreateSerializer, TherapistSurveyResponseCreateSerializer, TherapistSurveyTextUpdateSerializer, TherapistSurveyWriteSerializer
from rest_framework import serializers

class TherapistSurveyRetrieveHttpSerializer(HttpSuccessResponseSerializer):
    data = TherapistSurveyFullReadSerializer()

class TherapistSurveyInnerListHttpSerializer(HttpPaginatedSerializer):
    results = TherapistSurveyMiniReadSerializer(many=True)

class TherapistSurveyListHttpSerializer(HttpSuccessResponseSerializer):
    data = TherapistSurveyInnerListHttpSerializer()

class TherapistSurveyWriteSuccessHttpSerializer(HttpSuccessResponseSerializer):
    data = TherapistSurveyWriteSerializer()

class TherapistSurveyWriteErrorWrapperHttpSerializer(serializers.Serializer):
    name = serializers.ListSerializer(child=serializers.CharField())
    image = serializers.ListSerializer(child=serializers.CharField())

class TherapistSurveyWriteErrorHttpSerializer(HttpErrorResponseSerializer):
    data = TherapistSurveyWriteErrorWrapperHttpSerializer()



#  ---------------- survey   questions
    
class TherapistSurveyQuestionListWrapperHttpSerializer(HttpPaginatedSerializer):
    results = TherapistSurveyQuestionMiniReadSerializer(many=True)

class TherapistSurveyQuestionListHttpSerializer(HttpSuccessResponseSerializer):
    data = TherapistSurveyQuestionListWrapperHttpSerializer()

class TherapistSurveyQuestionRetrieveMCQSerializer(TherapistSurveyQuestionFullReadSerializer):
    schema = SurveyMCQQuestionSchemaSerializer()

class TherapistSurveyQuestionRetireveMCQHttpSerializer(HttpSuccessResponseSerializer):
    data = TherapistSurveyQuestionRetrieveMCQSerializer()

class TherapistSurveyQuestionRetrieveTextSerializer(TherapistSurveyQuestionFullReadSerializer):
    schema = SurveyTextQuestionSchemaSerializer()

class TherapistSurveyQuestionRetrieveTextHttpSerializer(HttpSuccessResponseSerializer):
    data = TherapistSurveyQuestionRetrieveTextSerializer()

class TherapistSurveyQuestionCreateErrorSerializer(serializers.Serializer):
    error = serializers.ListSerializer(child=serializers.CharField(), allow_null=True)
    schema = serializers.ListSerializer(child=serializers.CharField(), allow_null=True)
    description = serializers.ListSerializer(child=serializers.CharField(), allow_null=True)
    survey = serializers.ListSerializer(child=serializers.CharField(), allow_null=True)

class TherapistSurveyQuestionCreateHttpErrorSerializer(HttpErrorResponseSerializer):
    data = TherapistSurveyQuestionCreateErrorSerializer()

class TherapistSurveyQuestioUpdateErrorSerializer(serializers.Serializer):
    error = serializers.ListSerializer(child=serializers.CharField(), allow_null=True)
    schema = serializers.ListSerializer(child=serializers.CharField(), allow_null=True)
    description = serializers.ListSerializer(child=serializers.CharField(), allow_null=True)

class TherapistSurveyQuestionUpdateHttpErrorSerializer(HttpErrorResponseSerializer):
    data = TherapistSurveyQuestioUpdateErrorSerializer()


class TherapistSurveyQuestionCreateMCQHttpSerializer(HttpSuccessResponseSerializer):
    data = TherapistSurveyQuestionMCQCreateSerializer()

class TherapistSurveyQuestionUpdateMCQHttpSerializer(HttpSuccessResponseSerializer):
    data = TherapistSurveyMCQUpdateSerializer()

class TherapistSurveyQuestionCreateTextHttpSerializer(HttpSuccessResponseSerializer):
    data = TherapistSurveyQuestionTextCreateSerializer()

class TherapistSurveyQuestionUpdateTextHttpSerializer(HttpSuccessResponseSerializer):
    data = TherapistSurveyTextUpdateSerializer()


# ---------------- survey responses
    

class TherapistSurveyResponseListWrapperHttpSerializer(HttpPaginatedSerializer):
    results = TherapistSurveyMiniReadSerializer(many=True)

class TherapistSurveyResponseListHttpSerializer(HttpSuccessResponseSerializer):
    data = TherapistSurveyResponseListWrapperHttpSerializer()

class TherapistSurveyResponseRetrieveHttpSerializer(HttpSuccessResponseSerializer):
    data = TherapistSurveyFullReadSerializer()

class TherapistSurveyResponseCreateErrorSerializer(serializers.Serializer):
    error = serializers.ListSerializer(child=serializers.CharField(), allow_null=True)
    survey = serializers.ListSerializer(child=serializers.CharField(), allow_null=True)
   

class TherapistSurveyResponseCreateHttpErrorSerializer(HttpErrorResponseSerializer):
    data = TherapistSurveyResponseCreateErrorSerializer()

class TherapistSurveyResponseCreateHttpSerializer(HttpSuccessResponseSerializer):
    data = TherapistSurveyResponseCreateSerializer()
