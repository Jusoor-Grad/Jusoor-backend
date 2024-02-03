from rest_framework import serializers


class HttpResponeSerializer(serializers.Serializer):
        message = serializers.CharField()
        status = serializers.CharField()
        data = serializers.CharField()