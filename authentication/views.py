from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from sqlalchemy import desc
from authentication.mixins import ActionBasedPermMixin
from core.http import FormattedResponse, FormattedValidationError
from core.mixins import SerializerMapperMixin
from .serializers import HttpLoginResponseSerializer, HttpTokenRefreshResponseSerializer, HttpUserReadResponseSerializer, LoginResponseSerializer, TokenRefreshBodySerializer, UserLoginSerializer, PatientSignupSerializer, UserReadSerializer
from .services.auth import AuthService
from .constants.placeholders import INVALID_CREDENTIALS, LOGGED_IN, SIGNED_OUT, SIGNED_UP, TOKEN_INVALID, TOKEN_REFRESHED
from core.placeholders import ERROR, SUCCESS, CREATED
from django.contrib.auth import authenticate, login
from core.serializers import HttpResponeSerializer
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import RetrieveModelMixin
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken


import rest_framework.status as status
from drf_yasg.utils import swagger_auto_schema

class AuthViewset(ActionBasedPermMixin, SerializerMapperMixin, GenericViewSet):
    """View for basic authentication functionality"""


    action_permissions = {
        'login': [AllowAny],
        'signup': [AllowAny],
        'logout': [IsAuthenticated]
    }
    serializer_class_by_action = {
        'login': UserLoginSerializer,
        'signup': PatientSignupSerializer
    }


    @swagger_auto_schema(responses={status.HTTP_200_OK: HttpLoginResponseSerializer(),
    status.HTTP_401_UNAUTHORIZED: HttpResponeSerializer()},
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
            return FormattedResponse(
                status=status.HTTP_401_UNAUTHORIZED, message= INVALID_CREDENTIALS, data=None,
                )
        login(request, user) ## used to track login timestamp in DB
        # 3. generate the JWT token
        tokens = AuthService.generate_tokens(user)

        # 4. return the tokens
        return FormattedResponse(data=tokens.model_dump(),
        message= LOGGED_IN, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(responses= {status.HTTP_200_OK: PatientSignupSerializer})
    @action(methods=['POST'], detail=False)
    def signup(self, request):
        """signup a new user using his email and password"""

        # 1. extract the incoming HTTP body
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data

        # 2. create the user
        user = AuthService.signup(data['email'], data['password'], data['username'])
        # TODO: send a verification email to the user before activating his account
        # 3. generate the JWT token
        tokens = AuthService.generate_tokens(user)

        # 4. return the tokens
        return FormattedResponse(message=SIGNED_UP, status=status.HTTP_200_OK)

    @swagger_auto_schema(responses={status.HTTP_200_OK: HttpResponeSerializer()})
    @action(methods=['POST'], detail=False)
    def logout(self, request):
        """logout a user by blacklisting his refresh token"""
        AuthService.logout(request.data['refresh'])
        return FormattedResponse(status=status.HTTP_200_OK)

class TokenViewset(ActionBasedPermMixin, SerializerMapperMixin, GenericViewSet):

    action_permissions = {
        'verify': [AllowAny],
        'refresh': [AllowAny]
    }

    serializer_class_by_action = {
        'verify': TokenRefreshBodySerializer,
        'refresh': TokenRefreshBodySerializer 
    }

    @swagger_auto_schema(responses={status.HTTP_200_OK: HttpTokenRefreshResponseSerializer()})
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
            raise FormattedValidationError(TOKEN_INVALID)


        return FormattedResponse(data=tokens.model_dump(), message=TOKEN_REFRESHED, status=status.HTTP_201_CREATED)


    @swagger_auto_schema(responses={status.HTTP_200_OK: HttpTokenRefreshResponseSerializer()})
    @action(methods=['POST'], detail=False)
    def validate(self, request):
        

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data

        try:
            AuthService.validate_refresh_token(data['refresh_token'])
        except (InvalidToken, TokenError) as e:
            raise FormattedValidationError(TOKEN_INVALID)
        
        return FormattedResponse(data={'refresh_token': data['refresh_token']}, status=status.HTTP_200_OK)




class UserViewset(SerializerMapperMixin, GenericViewSet):

    serializer_class_by_action = {
        'profile': UserReadSerializer
    }

    pagination_class = None


    @swagger_auto_schema(responses={status.HTTP_200_OK: HttpUserReadResponseSerializer()},manual_parameters=None)
    @action(methods=['GET'], detail=False)
    def profile(self, request, *args, **kwargs):

        serializer = self.get_serializer(request.user)
        return FormattedResponse(data=serializer.data, status=status.HTTP_200_OK)