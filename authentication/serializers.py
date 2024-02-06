
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import Token
from rest_framework import serializers
from authentication.models import User
from core.http import ValidationError
from core.models import KFUPMDepartment, StudentPatient
from core.placeholders import DEPARTMENT_DOES_NOT_EXIST
from core.serializers import HttpResponeSerializer
from .services.encryption import AESEncryptionService

class UserLoginSerializer(serializers.Serializer):
	"""Serializer used for login credential validation on data level"""

	email = serializers.EmailField(allow_blank=False, max_length=150)
	password = serializers.CharField(allow_blank=False, max_length=128)

class PatientSignupSerializer(serializers.Serializer):
	"""Serializer used for signup credential validation on data level"""
	
	email = serializers.EmailField(allow_blank=False, max_length=150)
	username = serializers.CharField(allow_blank=False, max_length=150)
	password = serializers.CharField(allow_blank=False, max_length=128)
	department = serializers.CharField(allow_blank=False, max_length=10)

	def validate_department(self, value:str):
		"""Verifying that a department exists within valid KFUPM departments in the DB"""
		
		if not KFUPMDepartment.objects.filter(short_name=value).exists():

			raise ValidationError(DEPARTMENT_DOES_NOT_EXIST)

		return value


class TokenResponseSerializer(serializers.Serializer):
	"""Serializer used for login response validation on data level"""
	
	access = serializers.CharField()
	refresh = serializers.CharField()

class HttpTokenResponseSerializer(HttpResponeSerializer):
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

	def to_representation(self, instance):
		result =  super().to_representation(instance)

		aes = AESEncryptionService()

		result['username'] = aes.decrypt(result['username'])
		result['email'] = aes.decrypt(result['email'])

		return result

	class Meta:
		model = User
		fields = ['id', 'username', 'email']

class PatientReadSerializer(UserReadSerializer):

	department = serializers.SerializerMethodField()


	def get_department(self, instance):
		return instance.patient_profile.department.short_name
	class Meta:

		model = User
		
		fields = ['id', 'username', 'email', 'department']
		

class HttpPatientReadResponseSerializer(HttpResponeSerializer):
	data = PatientReadSerializer()


class TherapistReadSerializer(UserReadSerializer):

	speciality = serializers.SerializerMethodField()
	bio = serializers.SerializerMethodField()

	def get_speciality(self, instance):
		return instance.therapist_profile.speciality

	def get_bio(self, instance):
		return instance.therapist_profile.bio

	
	class Meta:

		model = User
		
		fields = ['id', 'username', 'email', 'bio', 'speciality']
		

class HttpTherapistReadResponseSerializer(HttpResponeSerializer):
	data = TherapistReadSerializer()