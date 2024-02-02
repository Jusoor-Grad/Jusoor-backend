from operator import is_
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework_simplejwt.tokens import RefreshToken
from core.http import FormattedValidationError as ValidationError
from ..constants.types import TokenPayload
from ..constants.placeholders import DUPLICATE_CREDENTIALS
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from authentication.services.encryption import AESEncryptionService as AES
from .hash import hash_string


User = get_user_model()
class AuthService:



    
    def signup(email: str, password: str, username: str) -> User:
        """Create a new user with the given email and password"""
        if User.objects.filter(Q(hashed_email= hash_string(email))).exists():
            raise ValidationError(DUPLICATE_CREDENTIALS)

        
        user = User.objects.create_user(username=username, email=email, password=password)
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
        


