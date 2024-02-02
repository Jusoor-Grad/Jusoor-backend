from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from authentication.mixins import ActionBasedPermMixin
from core.http import FormattedResponse
from core.mixins import SerializerMapperMixin
from .serializers import UserLoginSerializer, UserSignupSerializer
from .services.auth import AuthService
from .constants.placeholders import INVALID_CREDENTIALS, LOGGED_IN, SIGNED_OUT, SIGNED_UP
from core.placeholders import ERROR, SUCCESS, CREATED
from django.contrib.auth import authenticate, login


import rest_framework.status as status
from drf_yasg.utils import swagger_auto_schema

class AuthView(ActionBasedPermMixin, SerializerMapperMixin, ViewSet):
    """View for basic authentication functionality"""


    action_permissions = {
        'login': [AllowAny],
        'signup': [AllowAny],
        'logout': [IsAuthenticated]
    }
    serializer_class_by_action = {
        'login': UserLoginSerializer,
        'signup': UserSignupSerializer
    }


    @swagger_auto_schema(responses= {status.HTTP_200_OK: UserLoginSerializer})
    @action(methods=['POST'], detail=False)
    def login(self, request):
        """login a new user using his email and password"""
   
        # 1. extract the incoming HTTP body
        serializer = self.get_serializer_class()(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        
        # 2. authenticate the user
        user = authenticate(request=request, username=data['email'], password=data['password'])
        if user is None:
            return FormattedResponse(
                status=status.HTTP_401_UNAUTHORIZED,message= INVALID_CREDENTIALS, data= None,
                )
        login(request, user) ## used to track login timestamp in DB
        # 3. generate the JWT token
        tokens = AuthService.generate_tokens(user)

        # 4. return the tokens
        return FormattedResponse(data=tokens.model_dump(),
        message= LOGGED_IN, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(responses= {status.HTTP_200_OK: UserSignupSerializer})
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

    @action(methods=['POST'], detail=False)
    def logout(self, request):
        """logout a user by blacklisting his refresh token"""
        AuthService.logout(request.data['refresh'])
        return FormattedResponse(status=status.HTTP_200_OK)
