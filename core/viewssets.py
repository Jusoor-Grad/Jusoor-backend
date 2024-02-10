from rest_framework import viewsets
from authentication.mixins import ActionBasedPermMixin

from core.mixins import QuerysetMapperMixin, SerializerMapperMixin
from core.renderer import FormattedJSONRenderrer

class AugmentedViewSet(SerializerMapperMixin, ActionBasedPermMixin, QuerysetMapperMixin, viewsets.GenericViewSet):
    
    renderer_classes = [FormattedJSONRenderrer]
    filterset_fields = None