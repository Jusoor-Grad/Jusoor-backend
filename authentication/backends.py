"""
    Custom authnetication backends used for user lookup
"""

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

from authentication.services.hash import hash_string


class HashedEmailAuthBackend(BaseBackend):
    """
    Custom authentication backend for encrypted user lookup
    """
    def authenticate(self, request, username=None, password=None):
        """
        Authenticate the user by looking up the email hash
        """

        username = hash_string(username)
        user = get_user_model().objects.get(hashed_email=username)

        if user.check_password(password):
            return user
        return None

    def get_user(self, user_id):
        """
        Get the user through his ID
        """
        user = get_user_model().objects.get(id=user_id)
        return user