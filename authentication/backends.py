"""
    Custom authnetication backends used for user lookup
"""

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

from authentication.services.hash import hash_string


class EmailAuthBackend(BaseBackend):
    """
    Custom authentication backend for email-based auth
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate the user by looking up the email hash
        """
        
        ## blocking anyone from using a bot account to login
        user = get_user_model().objects.filter(email=username.lower(), is_bot=False)
        
        if not user:
            return None
        
        user = user.first()
        
        if user.check_password(password):
            return user
        
        return None

    def get_user(self, user_id):
        """
        Get the user through his ID
        """
        user = get_user_model().objects.get(id=user_id)
        return user