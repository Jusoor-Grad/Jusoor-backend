from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from sqlalchemy import desc
from authentication.mixins import ActionBasedPermMixin
from authentication.permissions import IsPatient, IsTherapist
from core.http import Response, ValidationError
from core.mixins import SerializerMapperMixin
from core.viewssets import AugmentedViewSet

from .serializers import HttpLoginErrorSerializer, HttpSignupErrorSerializer, HttpTokenResponseSerializer, HttpTherapistReadResponseSerializer, HttpTokenRefreshResponseSerializer, HttpPatientReadResponseSerializer, TokenResponseSerializer, TherapistReadSerializer, TokenRefreshBodySerializer, UserLoginSerializer, PatientSignupSerializer, PatientReadSerializer
from .services.auth import AuthService, User
from .constants.placeholders import INVALID_CREDENTIALS, LOGGED_IN, SIGNED_OUT, SIGNED_UP, TOKEN_INVALID, TOKEN_REFRESHED
from core.placeholders import ERROR, SUCCESS, CREATED
from django.contrib.auth import authenticate, login
from core.serializers import HttpErrorResponseSerializer, HttpSuccessResponseSerializer
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import UpdateModelMixin
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.utils.translation import gettext as _

import rest_framework.status as status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class AuthViewset(ActionBasedPermMixin, SerializerMapperMixin, GenericViewSet):
    """View for basic authentication functionality"""


    action_permissions = {
        'login': [AllowAny],
        'signup': [AllowAny],
        'logout': [AllowAny]
    }
    serializer_class_by_action = {
        'login': UserLoginSerializer,
        'signup': PatientSignupSerializer
    }


    @swagger_auto_schema(responses=
    {status.HTTP_200_OK: HttpTokenResponseSerializer(),
    status.HTTP_401_UNAUTHORIZED: HttpErrorResponseSerializer(),
    status.HTTP_400_BAD_REQUEST: HttpLoginErrorSerializer()},
    )
    @action(methods=['POST'], detail=False)
    def login(self, request):
        """
        login a new user using his email and password
        """
        # 1. extract the incoming HTTP body
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        
        # 2. authenticate the user
        user = authenticate(request=request, username=data['email'], password=data['password'])

        if user is None:
            return Response(
                status=status.HTTP_401_UNAUTHORIZED, message= INVALID_CREDENTIALS, data=None,
                )
        login(request, user, 'authentication.backends.EmailAuthBackend') ## used to track login timestamp in DB
        # 3. generate the JWT token
        tokens = AuthService.generate_tokens(user)

        # 4. return the tokens
        return Response(data=tokens.model_dump(),
        message= LOGGED_IN, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(responses= {status.HTTP_200_OK: HttpTokenResponseSerializer(), status.HTTP_400_BAD_REQUEST: HttpSignupErrorSerializer() })
    @action(methods=['POST'], detail=False)
    def signup(self, request):
        """signup a new user using his email and password"""

        # 1. extract the incoming HTTP body
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data

        # 2. create the user
        user = AuthService.patient_signup(email=data['email'], password=data['password'], username=data['username'])
        # TODO: send a verification email to the user before activating his account
        # 3. generate the JWT token
        login(request, user, 'authentication.backends.EmailAuthBackend') ## used to track login timestamp in DB
        # 3. generate the JWT token
        tokens = AuthService.generate_tokens(user)

        # 4. return the tokens
        return Response(data=tokens.model_dump(),
        message= SIGNED_UP, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={status.HTTP_200_OK: HttpSuccessResponseSerializer()}, request_body= openapi.Schema(type=openapi.TYPE_OBJECT, properties={'refresh': openapi.Schema(type=openapi.TYPE_STRING)}) )
    @action(methods=['POST'], detail=False)
    def logout(self, request):
        """logout a user by blacklisting his refresh token"""
        try:
            AuthService.logout(request.data['refresh'])
        except:
            raise ValidationError(TOKEN_INVALID)

        return Response(message=_('Logged out successfully.'), status=status.HTTP_200_OK)

class TokenViewset(ActionBasedPermMixin, SerializerMapperMixin, GenericViewSet):

    action_permissions = {
        'verify': [AllowAny],
        'refresh': [AllowAny]
    }

    serializer_class_by_action = {
        'verify': TokenRefreshBodySerializer,
        'refresh': TokenRefreshBodySerializer 
    }

    @swagger_auto_schema(responses={status.HTTP_200_OK: HttpTokenRefreshResponseSerializer(), status.HTTP_400_BAD_REQUEST: HttpErrorResponseSerializer()})
    @action(methods=['POST'], detail=False)
    def refresh(self, request):
        """
            Refreshing both access and refresh tokens given a refresh token
        """

        # serialize incoming payload

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.data
        
        # create a new pair of tokens after validating token
        try:
            AuthService.validate_refresh_token(data['refresh_token'])
            tokens = AuthService.generate_tokens(user=request.user)
            # blacklist old token
            AuthService.logout(data['refresh_token'])
        except (InvalidToken, TokenError) as e:
            raise ValidationError(TOKEN_INVALID)


        return Response(data=tokens.model_dump(), message=TOKEN_REFRESHED, status=status.HTTP_201_CREATED)


    @swagger_auto_schema(responses={status.HTTP_200_OK: HttpTokenRefreshResponseSerializer()})
    @action(methods=['POST'], detail=False)
    def verify(self, request):
        

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data

        try:
            AuthService.validate_refresh_token(data['refresh_token'])
        except (InvalidToken, TokenError) as e:
            raise ValidationError(TOKEN_INVALID)
        
        return Response(data={'refresh_token': data['refresh_token']}, status=status.HTTP_200_OK)




class UserViewset(SerializerMapperMixin, ActionBasedPermMixin, GenericViewSet):

    serializer_class_by_action = {
        'patient_profile': PatientReadSerializer,
        'therapist_profile': TherapistReadSerializer
    }

    action_permissions = {
        'patient_profile': [IsPatient() | IsTherapist()],
        'therapist_profile': [IsAuthenticated]
    }

    pagination_class = None

    def get_queryset(self):
        return super().get_queryset().filter(id=self.request.user.id).prefetch_related('patient_profile__department', 'therapist_profile__specializations__specialization')

    # TODO: update serializer for both therapists and patients

    @swagger_auto_schema(responses={status.HTTP_200_OK: HttpPatientReadResponseSerializer()},manual_parameters=None)
    @action(methods=['GET'], detail=False, url_path='patient', url_name='patient')
    def patient_profile(self, request, *args, **kwargs):
        """
            endpoint used to get the personal profile of the patient
            using his authneticated user profile
        """

        serializer = self.get_serializer(request.user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={status.HTTP_200_OK: HttpTherapistReadResponseSerializer()},manual_parameters=None)
    @action(methods=['GET'], detail=False, url_path='therapist', url_name='therapist')
    def therapist_profile(self, request, *args, **kwargs):
        """
            endpoint used to ger the personal profile of the therapist
            using the token header
        """
        
        serializer = self.get_serializer(instance=request.user)
        return Response(data=serializer.data, status=status.HTTP_200_OK)