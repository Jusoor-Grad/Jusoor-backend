"""
All authnetication-related databsase schema defintions
"""
from collections.abc import Iterable
from enum import unique
from typing import Any
from django.db import models
from django.contrib.auth.models import AbstractUser

from core.models import TimeStampedModel
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.validators import UnicodeUsernameValidator

class User(AbstractUser, TimeStampedModel):
    """
    Model to add extra fields to the default django user model
    """
    image = models.ImageField(upload_to='users', null=True, blank=True)


    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _("username"),
        max_length=150,
        unique=False,
        help_text=_(
            "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
        ),
        validators=[username_validator],
        error_messages={
            "unique": _("A user with that username already exists."),
        },
    )
    email = models.EmailField(verbose_name=_("email address"), blank=True, unique=True)
    # whether or not the user is a bot
    is_bot = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self) -> str:
        return f'USERNAME: {self.username}, EMAIL: {self.email}'

# specialized user roles

