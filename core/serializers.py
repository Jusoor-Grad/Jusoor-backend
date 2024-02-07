from rest_framework import serializers



#  ------- Utility serializers ---------
class HttpSuccessResponeSerializer(serializers.Serializer):
        message = serializers.CharField()
        status = serializers.IntegerField()
        data = serializers.CharField()

# ------- model serializers ---------

class HttpErrorSerializer(serializers.Serializer):
    errors = serializers.DictField(child=serializers.CharField())

class HttpErrorResponseSerializer(serializers.Serializer):
    status = serializers.IntegerField()
    message = serializers.CharField()
    data = HttpErrorSerializer()
