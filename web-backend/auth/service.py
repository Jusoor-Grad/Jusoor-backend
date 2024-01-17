from django.contrib.auth.models import User
from django.db.models import Q
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ValidationError
from auth.types import TokenPayload
from auth.placeholders import DUPLICATE_CREDENTIALS

class AuthService:

    def login(email: str, password: str) -> User | None:
        """Authenticate user credentials and return the user object if authenticated, None otherwise"""
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            pass

        return None

    def signup(email: str, password: str, username: str) -> User:
        """Create a new user with the given email and password"""
        if User.objects.filter(Q(email=email) | Q(username=username)).exists():
            raise ValidationError({'message': DUPLICATE_CREDENTIALS})
        user = User.objects.create_user(username=username, email=email, password=password)
        return user

    def generate_tokens(user: User) -> TokenPayload:
        refresh_token = RefreshToken.for_user(user)

        return TokenPayload(
            refresh=str(refresh_token),
            access=str(refresh_token.access_token)
        )


