"""
    File used to create custom object managers for the models
"""
from django.db.models import Manager, QuerySet
from django.utils import timezone

from core.querysets import SoftDeletedQuerySet


class SoftDeletedManager(Manager):
    """
    Custom manager to exclude soft deleted objects from the queryset
    """

    def get_queryset(self):
        """
        Overriding the default get_queryset method to exclude soft deleted objects
        """
        return SoftDeletedQuerySet(self.model, using=self._db).filter(deleted_at__isnull=True)