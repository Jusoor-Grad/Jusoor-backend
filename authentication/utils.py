"""
all definitions of authnetication-based utilies
"""
from django.db import models
from typing import Optional, Callable
from rest_framework.permissions import BasePermission



OPTIONS_METHOD = "OPTIONS"

class ActionBasedPermission(BasePermission):
    """
    Custom permission that can accept/deny access for a specific action
    given the action_permissions mapping defined in the viewset
    """

    def has_permission(self, request, view):
        action_perms = getattr(view, "action_permissions", {})
        action = view.action
        class_list = []
        if action in action_perms:
            class_list = action_perms[action]
        else:
            return False

        perm_list = [perm() for perm in class_list]

        # debugging note: python maps are are generators that get *consumed*
        # so avoid printing it while debugging
        checks = map(lambda perm: perm.has_permission(request, view), perm_list)

        return all(checks)


def get_full_perm(model, action):
    """Utility to get the full name of a permission and its parent application"""
    model_name = model.__name__.lower()
    app_label = model._meta.app_label

    return "{}.{}_{}".format(app_label, action, model_name)

def HasPerm(action_name, model: Optional[models.Model] = None, ignore_super=False):
    """
    Takes an action_name, and returns a class with a
    has_permission() method that checks if the user has a permission named in format:
    '{applabel}_{action_name}_{model}'.
    """

    class Result(BasePermission):
        message = "ActionBasedError: You are not allowed to perform this action"

        def __init__(self, *args, **kwargs):
            self.model = model
            super().__init__(*args, **kwargs)

        def get_model(self, view):
            model = self.model
            if self.model is not None:
                return model

            serializer = view.get_serializer_class()
            if serializer is not None and hasattr(serializer, "Meta") and serializer.Meta is not None:
                model = serializer.Meta.model
            else:
                model = view.model

            return model

        def has_permission(self, request, view):
            # ignoring auth for options method
            if request.method == OPTIONS_METHOD:
                return True

            used_model = self.get_model(view)
            if used_model is None:
                raise Exception(f"ActionBasedError: Cannot guess model from given arguments: f{(action_name, model, request, view)}")

            full_name = get_full_perm(used_model, action_name)

            user = request.user

            # should never occur
            if user.is_anonymous:
                return False

            if ignore_super:
                model_name = used_model.__name__.lower()
                perm = "{}_{}".format(action_name, model_name)
                res = user.has_perm_ignore_super(perm)
            else:
                res = user.has_perm(full_name)

            return res

    return Result


def HasLambdaPerm(function: Callable):
    """
    a permission class that uses a custom passed function to control access on runtime
    @function a function that takes a request, and view objects and returns a boolean
    """

    class Result(BasePermission):
        def has_permission(self, request, view):
            return function(request, view)

    return Result