"""
An agregation of all DRF mixin class general-purposee utilities
"""

from rest_framework import serializers

class SerializerMapperMixin:
    """
    utility mixin used to assign a different serializer class for each action
    """

    serializer_class = None
    serializer_class_by_action = dict()

    def get_serializer_class(self) -> serializers.Serializer:
        if hasattr(self, "serializer_class_by_action"):
            serializer_class = self.serializer_class_by_action.get(self.action, self.serializer_class)

            if self.serializer_class is None and serializer_class is None:
                print("WARNING: You may need to either provide a default serializer class or add a serializer mapping to invoked method")

        return serializer_class

class QuerysetMapperMixin:
    """
    utility mixin used to assign a different queryset for each action
    """

    queryset = None
    queryset_by_action = dict()

    def get_queryset(self):
        if hasattr(self, "queryset_by_action"):
            queryset = self.queryset_by_action.get(self.action, self.queryset)

            if self.queryset is None and queryset is None:
                print("WARNING: You may need to either provide a default queryset or add a queryset mapping to invoked method")

        return queryset



