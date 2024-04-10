from rest_framework import serializers
from core.models import KFUPMDepartment


#  ------- Utility serializers ---------
class HttpSuccessResponseSerializer(serializers.Serializer):
    """
    Serializer for non-paginated HTTP response
    """

    message = serializers.CharField()
    status = serializers.IntegerField()
    data = serializers.CharField()

class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()

class HttpSuccessResponseNestedMessageSerializer(serializers.Serializer):
    """
    Serializer for non-paginated HTTP response
    """

    message = serializers.CharField()
    status = serializers.IntegerField()
    data = MessageSerializer()
    
class HttpPaginatedSerializer(serializers.Serializer):

    count = serializers.IntegerField()
    next = serializers.URLField(allow_null=True)
    previous = serializers.URLField(allow_null=True)
    results = serializers.ListField(child=serializers.DictField())

class HttpInnerErrorSerialzier(serializers.Serializer):
    error = serializers.ListSerializer(child=serializers.CharField())
class HttpErrorSerializer(serializers.Serializer):
    errors = HttpInnerErrorSerialzier

class HttpErrorResponseSerializer(serializers.Serializer):
    status = serializers.IntegerField()
    message = serializers.CharField()
    data = HttpErrorSerializer(allow_null=True)

class KFUPMDepartmentSerializer(serializers.ModelSerializer):
    """Serializer for KFUPMDepartment"""
    class Meta:
        model = KFUPMDepartment
        fields = ['id', 'short_name', 'long_name']


class HttpKFUPMDepartmentResponseSerializer(HttpPaginatedSerializer):
    results = KFUPMDepartmentSerializer(many=True)

class HttpKFUPMDepartmentRetrieveResponseSerializer(HttpSuccessResponseSerializer):
    data = KFUPMDepartmentSerializer()

class PaginatedKFUPMDeptResponseSerializer(HttpPaginatedSerializer):
    results= KFUPMDepartmentSerializer(many=True)

class HttpKFUPMDepartmentListResponseSerializer(HttpSuccessResponseSerializer):
    data = PaginatedKFUPMDeptResponseSerializer()


class TherapistSpecializationSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()

class CounterSerializer(serializers.Serializer):
    current_count = serializers.IntegerField()
    last_month_count = serializers.IntegerField()

class HttpCounterSerializer(HttpSuccessResponseSerializer):
    data = CounterSerializer()