from rest_framework import serializers


class HttpResponeSerializer(serializers.Serializer):
        message = serializers.CharField()
        status = serializers.IntegerField()
        data = serializers.CharField()