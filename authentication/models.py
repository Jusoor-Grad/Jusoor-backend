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

class User(AbstractUser, TimeStampedModel):
    """
    Model to add extra fields to the default django user model
    """
    image = models.ImageField(upload_to='users', null=True, blank=True)
    

    def __str__(self) -> str:
        return f'USERNAME: {self.username}, EMAIL: {self.email}'

# specialized user roles

