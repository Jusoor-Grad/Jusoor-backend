from typing import List
from django.db.models import QuerySet, Q
from django.utils import timezone
from rest_framework.generics import GenericAPIView


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




def OwnedQuerySet( view: GenericAPIView, queryset: QuerySet, ownership_fields: List[str] = ['user'], user_model_rel: str = None):
    """
        Queryset filter action that only returns owned objects by the current user
    """
    
    user = view.request.user

    if user_model_rel is not None:
        user = getattr(user, user_model_rel)

    filters = Q(**{ownership_fields[0]: user})

    if len(ownership_fields) > 0:
        for field in ownership_fields[1:]:
            filters |= Q(**{field: user})

    print('FILTERING', filters)

    return queryset.filter(filters)