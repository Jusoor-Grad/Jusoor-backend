"""
    File used for storing auth-related translation placeholders
"""

from django.utils.translation import gettext_lazy as _


#  --------------- Errors ---------------

INVALID_CREDENTIALS = _("Invalid credentials")
DUPLICATE_CREDENTIALS = _("Duplicate Credentials")

#  --------------- ENV KEYS ---------------

SIMPLE_JWT_SIGNING_KEY = 'SIMPLE_JWT_SIGNING_KEY'

# --------------- Messages ---------------
LOGGED_IN = _("Logged in successfully")
SIGNED_UP = _("Signed up successfully")
SIGNED_OUT = _("Signed out successfully")
TOKEN_REFRESHED  = _('Token refreshed successfully')
TOKEN_VALID  = _('Token verified successfully')
TOKEN_INVALID  = _('Passed token is invalid')