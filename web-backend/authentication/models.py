"""
All authnetication-related databsase schema defintions
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
from core.models import TimeStampedModel

class User(AbstractUser, TimeStampedModel):
    """
    Model to add extra fields to the default django user model
    """
    image = models.ImageField(upload_to='users', null=True, blank=True)
    

    def __str__(self) -> str:
        return f'USERNAME{self.username}, EMAIL: {self.email}'

