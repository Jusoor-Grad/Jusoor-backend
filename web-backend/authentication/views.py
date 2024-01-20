from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from core.mixins import SerializerMapperMixin
from .serializers import UserLoginSerializer, UserSignupSerializer
from .services.auth import AuthService
from .placeholders import INVALID_CREDENTIALS
from core.placeholders import ERROR
import rest_framework.status as status
from drf_yasg.utils import swagger_auto_schema

class AuthView(SerializerMapperMixin, ViewSet):
    """View for basic authentication functionality"""


    permission_classes = [AllowAny]
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
        print(data)
        # 2. authenticate the user
        user = AuthService.login(data['email'], data['password'])
        if user is None:
            return Response({ERROR: INVALID_CREDENTIALS}, status=status.HTTP_401_UNAUTHORIZED)

        # 3. generate the JWT token
        tokens = AuthService.generate_tokens(user)

        # 4. return the tokens
        return Response(tokens.model_dump(), status=status.HTTP_200_OK)
    
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
        return Response(tokens.model_dump(), status=status.HTTP_200_OK)
