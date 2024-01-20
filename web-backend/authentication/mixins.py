
from auth.utils import ActionBasedPermission


class ActionBasedPermMixin:
    permission_classes = [ActionBasedPermission]