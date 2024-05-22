
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework_simplejwt.tokens import RefreshToken
from core.http import ValidationError as ValidationError
from core.models import StudentPatient
from ..constants.types import TokenPayload
from ..constants.placeholders import DUPLICATE_CREDENTIALS
from authentication.services.encryption import AES256EncryptionService as AES
from rest_framework_simplejwt.tokens import UntypedToken
from django.db import transaction

User = get_user_model()
class AuthService:


    @transaction.atomic
    def patient_signup(email: str, password: str, username: str):
        """Create a new patient profile with the given email and password"""
        if User.objects.filter(Q(email= email.lower())).exists():
            raise ValidationError(DUPLICATE_CREDENTIALS)

        patient, user = StudentPatient.create(username, email.lower(), password)
        
        return user

    def generate_tokens(user) -> TokenPayload:
        """Generate a new refresh and access token for the given user"""
        refresh_token = RefreshToken.for_user(user)
        
        return TokenPayload(
            refresh=str(refresh_token),
            access=str(refresh_token.access_token)
        )

    def logout(refresh_token: str):
        """logout a user by blacklisting the given user refresh token"""
        refresh_token = RefreshToken(refresh_token)
        refresh_token.blacklist()

    def validate_refresh_token(refresh_token: str):
        """
            Validate a refresh token by checking current outstanding tokens and blacklisted tokens
        """
        return UntypedToken(refresh_token)
        

        
        


