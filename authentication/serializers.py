
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import Token
from rest_framework import serializers
from authentication.models import User
from core.http import ValidationError
from core.models import KFUPMDepartment, StudentPatient
from core.placeholders import DEPARTMENT_DOES_NOT_EXIST
from core.serializers import HttpPaginatedSerializer, HttpSuccessResponseSerializer, HttpErrorSerializer, TherapistSpecializationSerializer
from sentiment_ai.models import StudentPatientSentimentPosture
from sentiment_ai.serializers import StudentPatientSentimentPostureMiniReadSerializer
from .services.encryption import AESEncryptionService
from drf_yasg.utils import swagger_serializer_method
from django.utils.translation import get_language
from drf_yasg.utils import swagger_serializer_method

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

class PatientRetrieveSerializer(UserReadSerializer):

	department = serializers.SerializerMethodField()
	appointments_count = serializers.SerializerMethodField()
	sentiment_timeline = serializers.SerializerMethodField()

	def get_department(self, instance):

		if instance.patient_profile.department is None:
			return None
		
		return instance.patient_profile.department.short_name

	def get_appointments_count(self, instance):
		return 	instance.patient_profile.appointments.count()
	
	@swagger_serializer_method(serializer_or_field=StudentPatientSentimentPostureMiniReadSerializer(many=True))
	def get_sentiment_timeline(self, instance):
		"""return the last 7 sentiemnt postures for the user"""
		postures_count = StudentPatientSentimentPosture.objects.filter(patient=instance.patient_profile).count()
		postures = StudentPatientSentimentPosture.objects.filter(patient=instance.patient_profile).order_by('-date')[:min(7, postures_count)]

		return StudentPatientSentimentPostureMiniReadSerializer(postures, many=True).data

	class Meta:

		model = User
		
		fields = ['id', 'username', 'email', 'department', 'image', 'appointments_count', 'sentiment_timeline']		

class PatientReadSerializer(UserReadSerializer):

	department = serializers.SerializerMethodField()
	sentiment_posture = serializers.SerializerMethodField(allow_null=True)


	def get_department(self, instance):

		if instance.patient_profile.department is None:
			return None
		
		return instance.patient_profile.department.short_name
	
	@swagger_serializer_method(serializer_or_field=StudentPatientSentimentPostureMiniReadSerializer(many=False))
	def get_sentiment_posture(self, instance):

		last_posture = instance.patient_profile.sentiment_postures.order_by('date').last()
		if last_posture != None:
			return  StudentPatientSentimentPostureMiniReadSerializer(last_posture).data
		
		return None

	class Meta:

		model = User
		
		fields = ['id', 'username', 'email', 'department', 'image', 'sentiment_posture']
		

class HttpPatientReadResponseSerializer(HttpSuccessResponseSerializer):
	data = PatientReadSerializer()


class PaginatedPatientResponseSerializer(HttpPaginatedSerializer):
    results = PatientReadSerializer(many=True)

class PatientHttpListResposneSerializer(HttpSuccessResponseSerializer):
	data = PaginatedPatientResponseSerializer()

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