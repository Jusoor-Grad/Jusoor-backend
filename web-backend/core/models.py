"""
General utility DB models
"""

from django.db import models

# Create your models here.


class TimeStampedModel(models.Model):
    """
    Abstract model to add created_at and updated_at fields to all models
    """
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        """
        Meta class for the model
        """
        abstract = True
