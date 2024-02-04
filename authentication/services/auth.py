from operator import is_
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from core.http import FormattedValidationError as ValidationError
from core.models import StudentPatient
from ..constants.types import TokenPayload
from ..constants.placeholders import DUPLICATE_CREDENTIALS, TOKEN_INVALID
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from authentication.services.encryption import AESEncryptionService as AES
from .hash import hash_string
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.tokens import UntypedToken

User = get_user_model()
class AuthService:



    
    def patient_signup(email: str, password: str, username: str, department: str) -> User:
        """Create a new patient profile with the given email and password"""
        if User.objects.filter(Q(hashed_email= hash_string(email))).exists():
            raise ValidationError(DUPLICATE_CREDENTIALS)

        
        user = User.objects.create_user(username=username, email=email, password=password)
        patient = StudentPatient.objects.create(user=user, department=department)
        # TODO: send a verification email to the user before activating his account
        return user

    def generate_tokens(user: User) -> TokenPayload:
        refresh_token = RefreshToken.for_user(user)
        
        return TokenPayload(
            refresh=str(refresh_token),
            access=str(refresh_token.access_token)
        )

    def logout(refresh_token: str):
        """Blacklist the given refresh token"""
        refresh_token = RefreshToken(refresh_token)
        refresh_token.blacklist()

    def validate_refresh_token(refresh_token: str):
        """
            Validate a refresh token by checking current outstanding tokens and blacklisted tokens
        """
        return UntypedToken(refresh_token)
        

        
        


