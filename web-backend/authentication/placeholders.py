"""
    File used for storing auth-related translation placeholders
"""

from django.utils.translation import gettext_lazy as _


#  --------------- Errors ---------------

INVALID_CREDENTIALS = _("INVALID_CREDENTIALS")
DUPLICATE_CREDENTIALS = _("DUPLICATE_CREDENTIALS")

#  --------------- ENV KEYS ---------------

SIMPLE_JWT_SIGNING_KEY = 'SIMPLE_JWT_SIGNING_KEY'