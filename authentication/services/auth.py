from operator import is_
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework_simplejwt.tokens import RefreshToken
from core.http import FormattedValidationError as ValidationError
from ..types import TokenPayload
from ..placeholders import DUPLICATE_CREDENTIALS
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from authentication.services.encryption import AESEncryptionService as AES
from .hash import hash_string

User = get_user_model()
class AuthService:

    # TODO: force MFA on login for users who are classified as therapists
    def login(email: str, password: str) -> User | None:
        """Authenticate user credentials and return the user object if authenticated, None otherwise"""
       
        try:
            aes = AES()
            email = hash_string(email)
            print(email)
            user = User.objects.get(hashed_email=email)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            pass

        return None

    
    def signup(email: str, password: str, username: str) -> User:
        """Create a new user with the given email and password"""
        if User.objects.filter(Q(email=email) | Q(username=username)).exists():
            raise ValidationError(DUPLICATE_CREDENTIALS)

        # encrypt the username and email, and hashing the email for deterministic lookup
        aes = AES()
        username = aes.encrypt(username)
        hashed_email = hash_string(email)
        email = aes.encrypt(email)

        
        user = User.objects.create_user(username=username, email=email, hashed_email=hashed_email, password=password)
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
        


