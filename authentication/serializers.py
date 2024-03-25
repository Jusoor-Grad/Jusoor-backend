
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import Token
from rest_framework import serializers
from authentication.models import User
from core.http import ValidationError
from core.models import KFUPMDepartment, StudentPatient
from core.placeholders import DEPARTMENT_DOES_NOT_EXIST
from core.serializers import HttpPaginatedSerializer, HttpSuccessResponseSerializer, HttpErrorSerializer, TherapistSpecializationSerializer
from .services.encryption import AESEncryptionService
from drf_yasg.utils import swagger_serializer_method
from django.utils.translation import get_language
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

class HttpTokenResponseSerializer(HttpSuccessResponseSerializer):
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

		if instance.patient_profile.department is None:
			return None
		
		return instance.patient_profile.department.short_name
	class Meta:

		model = User
		
		fields = ['id', 'username', 'email', 'department', 'image']
		

class HttpPatientReadResponseSerializer(HttpSuccessResponseSerializer):
	data = PatientReadSerializer()


class HttpPatientListResponseSerializer(HttpPaginatedSerializer):
    results = PatientReadSerializer(many=True)

class TherapistReadSerializer(UserReadSerializer):

	bio = serializers.SerializerMethodField()
	specializations = serializers.SerializerMethodField()

	def get_bio(self, instance):
		return instance.therapist_profile.bio

	@swagger_serializer_method(serializer_or_field=TherapistSpecializationSerializer(many=True))
	def get_specializations(self, instance):

		if get_language() == 'ar':
			return [{'name': spec.specialization.name_ar, 'description': spec.specialization.description_ar} for spec in instance.therapist_profile.specializations.all()]
		elif get_language() == 'en':
			return [{'name': spec.specialization.name_en, 'description': spec.specialization.description_en} for spec in instance.therapist_profile.specializations.all()]
		else:
			return [{'name': spec.specialization.name_en, 'description': spec.specialization.description_en} for spec in instance.therapist_profile.specializations.all()]
	
	class Meta:

		model = User	
		fields = ['id', 'username', 'email', 'bio', 'image', 'specializations']


class TherapistMinifiedReadSerializer(TherapistReadSerializer):

	class Meta:

		model = User
		fields = ['id', 'username', 'image']

class HttpTherapistReadResponseSerializer(HttpSuccessResponseSerializer):
	data = TherapistReadSerializer()

class HttpTherapistListResponseSerializer(HttpPaginatedSerializer):
    results = TherapistReadSerializer(many=True)