
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import Token
from rest_framework import serializers


# TODO: discard this serializer since it does not work at all
class TokenPermInjectorSerializer(TokenObtainPairSerializer):
    """Customer serializer used to inject user permissions into the JWT token customer claims"""
    
    @classmethod
    def get_token(cls, user: get_user_model()) -> Token:
        
        # 1.  getting serializer token dictionary
        token =  super().get_token(user)
        # 2.  injecting user permissions into the token dictionary
        token['permissions'] = list(user.get_all_permissions())
        return token

class UserLoginSerializer(serializers.Serializer):
    """Serializer used for login credential validation on data level"""

    email = serializers.EmailField(allow_blank=False, max_length=150)
    password = serializers.CharField(allow_blank=False, max_length=128)

class UserSignupSerializer(serializers.Serializer):
    """Serializer used for signup credential validation on data level"""
    
    email = serializers.EmailField(allow_blank=False, max_length=150)
    username = serializers.CharField(allow_blank=False, max_length=150)
    password = serializers.CharField(allow_blank=False, max_length=128)