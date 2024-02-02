"""
    File used to create custom object managers for the models
"""
from django.db.models import Manager, QuerySet
from django.utils import timezone

class SoftDeletedQuerySet(QuerySet):
    """
        Overriding standard queryset to remove all softly deleted records
    """

    def delete(self):
        """
        Overriding the default delete method to soft delete the objects
        """
        return super(SoftDeletedQuerySet, self).update(deleted_at=timezone.now())

    def hard_delete(self):
        """
        Method to permanently delete the objects from the database
        """
        return super(SoftDeletedQuerySet, self).delete()


class SoftDeletedManager(Manager):
    """
    Custom manager to exclude soft deleted objects from the queryset
    """

    def get_queryset(self):
        """
        Overriding the default get_queryset method to exclude soft deleted objects
        """
        return SoftDeletedQuerySet.filter(deleted_at__isnull=True)