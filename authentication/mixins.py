
from authentication.utils import ActionBasedPermission


class ActionBasedPermMixin:
    permission_classes = [ActionBasedPermission]

    action_permissions = {}