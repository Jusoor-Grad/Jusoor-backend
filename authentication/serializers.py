
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import Token
from rest_framework import serializers
from authentication.models import User
from core.http import ValidationError
from core.models import KFUPMDepartment, StudentPatient
from core.placeholders import DEPARTMENT_DOES_NOT_EXIST
from core.serializers import HttpPaginatedSerializer, HttpSuccessResponeSerializer, HttpErrorSerializer
from .services.encryption import AESEncryptionService

class UserLoginSerializer(serializers.Serializer):
	"""Serializer used for login credential validation on data level"""

	email = serializers.EmailField(allow_blank=False, max_length=150)
	password = serializers.CharField(allow_blank=False, max_length=128)

class LoginInnerWrapperSerializer(serializers.Serializer):
	"""Serializer used for login credential validation on data level"""
	email = serializers.ListSerializer(child=serializers.CharField(allow_blank=True, max_length=150))
	password = serializers.ListSerializer(child=serializers.CharField(allow_blank=True, max_length=128))
class LoginErrorWrapperSerializer(HttpErrorSerializer):
	errors = LoginInnerWrapperSerializer()

class HttpLoginErrorSerializer(HttpErrorSerializer):
	data = LoginErrorWrapperSerializer()

class PatientSignupSerializer(serializers.Serializer):
	"""Serializer used for signup credential validation on data level"""
	email = serializers.EmailField(allow_blank=False, max_length=150)
	username = serializers.CharField(allow_blank=False, max_length=150)
	password = serializers.CharField(allow_blank=False, max_length=128)

class SignupInnerWrapperSerializer(serializers.Serializer):
	"""Serializer used for Signup credential validation on data level"""
	email = serializers.ListSerializer(child=serializers.CharField(allow_blank=True, max_length=150), allow_null=True)
	username = serializers.ListSerializer(child=serializers.CharField(allow_blank=True, max_length=128), allow_null=True)
	password = serializers.ListSerializer(child=serializers.CharField(allow_blank=True, max_length=128), allow_null=True)
class SignupErrorWrapperSerializer(HttpErrorSerializer):
	errors = SignupInnerWrapperSerializer()

class HttpSignupErrorSerializer(HttpErrorSerializer):
	data = LoginErrorWrapperSerializer()

class TokenResponseSerializer(serializers.Serializer):
	"""Serializer used for login response validation on data level"""
	
	access = serializers.CharField()
	refresh = serializers.CharField()

class HttpTokenResponseSerializer(HttpSuccessResponeSerializer):
	data = TokenResponseSerializer()



# ------------- Token serializers ------------ #

class TokenRefreshBodySerializer(serializers.Serializer):
	refresh_token = serializers.CharField(allow_blank=False)

class TokenRefreshResponeSerializer(serializers.Serializer):
	refresh_token = serializers.CharField(allow_blank=False)
	access_token = serializers.CharField(allow_blank=False)


class HttpTokenRefreshResponseSerializer(serializers.Serializer):
	data = TokenRefreshResponeSerializer()

class HttpTokenVerifyResponseSerializer(serializers.Serializer):
	data = TokenRefreshBodySerializer()


# ----------- User serializers -------- #

class UserReadSerializer(serializers.ModelSerializer):
	"""
		Generic user serializer for reading unencryoted user data
	"""

	class Meta:
		model = User
		fields = ['id', 'username', 'email', 'image']

class PatientReadSerializer(UserReadSerializer):

	department = serializers.SerializerMethodField()


	def get_department(self, instance):
		return instance.patient_profile.department.short_name
	class Meta:

		model = User
		
		fields = ['id', 'username', 'email', 'department', 'image']
		

class HttpPatientReadResponseSerializer(HttpSuccessResponeSerializer):
	data = PatientReadSerializer()


class HttpPatientListResponseSerializer(HttpPaginatedSerializer):
    results = PatientReadSerializer(many=True)

class TherapistReadSerializer(UserReadSerializer):

	bio = serializers.SerializerMethodField()

	def get_bio(self, instance):
		return instance.therapist_profile.bio

	
	class Meta:

		model = User
		
		fields = ['id', 'username', 'email', 'bio', 'image']
		

class HttpTherapistReadResponseSerializer(HttpSuccessResponeSerializer):
	data = TherapistReadSerializer()