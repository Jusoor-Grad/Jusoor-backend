"""
All authnetication-related databsase schema defintions
"""
from collections.abc import Iterable
from typing import Any
from django.db import models
from django.contrib.auth.models import AbstractUser
from authentication.services.encryption import AESEncryptionService
from authentication.services.hash import hash_string
from core.models import TimeStampedModel

class User(AbstractUser, TimeStampedModel):
    """
    Model to add extra fields to the default django user model
    """
    image = models.ImageField(upload_to='users', null=True, blank=True)
    hashed_email = models.TextField(null=False, blank=False)



    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.__original_email = self.hashed_email or None
        self.__original_username = self.username or None
    

    def __str__(self) -> str:
        return f'USERNAME{self.username}, EMAIL: {self.email}'

    def save(self, *args, **kwargs) -> None:
        
        aes = AESEncryptionService()

        # if the object is newly created just encrypt the email and username
        if not self.id:

            self.username = aes.encrypt(self.username)
            self.__original_username = self.username

            self.hashed_email = hash_string(self.email)
            self.email = aes.encrypt(self.email)
            self.__original_email = self.hashed_email

          
        else:
            # for old objects, check if the email or username have changed and then encrypt them
            if (self.__original_email is None) or hash_string(self.email) != self.__original_email:
                self.email = aes.encrypt(self.email)
                self.hashed_email = hash_string(self.email)
                self.__original_email = self.hashed_email

            if (self.__original_username is None) or (self.username) != aes.decrypt(self.__original_username):
                self.username = aes.encrypt(self.username)
                self.__original_username = self.username
        
        return super().save(*args, **kwargs)



# specialized user roles

