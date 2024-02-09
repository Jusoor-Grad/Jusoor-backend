from rest_framework import serializers
from rest_framework.generics import GenericAPIView
from typing import Dict


#  ------- Utility serializers ---------
class HttpSuccessResponeSerializer(serializers.Serializer):
    """
    Serializer for non-paginated HTTP response
    """

    message = serializers.CharField()
    status = serializers.IntegerField()
    data = serializers.CharField()




class HttpPaginatedSerializer(serializers.Serializer):

    count = serializers.IntegerField()
    next = serializers.URLField()
    previous = serializers.URLField()
    results = serializers.ListField(child=serializers.DictField())


    



class HttpErrorSerializer(serializers.Serializer):
    errors = serializers.DictField(child=serializers.CharField())

class HttpErrorResponseSerializer(serializers.Serializer):
    status = serializers.IntegerField()
    message = serializers.CharField()
    data = HttpErrorSerializer()


