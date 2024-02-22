"""
An agregation of all DRF mixin class general-purposee utilities
"""
from ast import Call
from typing import Dict, Callable, Union
import django
from numpy import isin
from rest_framework import serializers
from django.db.models import QuerySet, Model

from core.querysets import QSWrapper
class SerializerMapperMixin:
	"""
	utility mixin used to assign a different serializer class for each action
	"""

	serializer_class = None
	serializer_class_by_action: Dict[str, serializers.Serializer] = dict()

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
	# a dictionary that either maps an action to a queryset or a callable that returns a queryset
	queryset_by_action: Dict[str, Union[QuerySet, Callable]] = dict()

	def get_queryset(self):
		if hasattr(self, "queryset_by_action"):
			action_qs = self.queryset_by_action.get(self.action, self.queryset)

			if isinstance(action_qs, QSWrapper):
				queryset = action_qs()(self)
			elif callable(action_qs):
				queryset = action_qs(self)
			else:
				queryset = action_qs

			if self.queryset is None and action_qs is None:
				print("WARNING: You may need to either provide a default queryset or add a queryset mapping to invoked method")

		return queryset



