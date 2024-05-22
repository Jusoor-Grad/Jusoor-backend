
from authentication.utils import ActionBasedPermission


class ActionBasedPermMixin:
    """DRF utility used to force per-viewset endpoint permissions"""
    permission_classes = [ActionBasedPermission]

    action_permissions = {}