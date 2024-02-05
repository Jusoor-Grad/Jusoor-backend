"""
    Permission definition for the core system
"""
from django.db.models import Model

from authentication.utils import HasLambdaPerm


def IsOwner(model: Model, ownership_field: str = 'user'):
    """
        Permission to only allow model owners to access
    """

    def validate_owner(request, view):
        return model.objects.filter(**{ownership_field: request.user.pk}).exists()

    return HasLambdaPerm(validate_owner)