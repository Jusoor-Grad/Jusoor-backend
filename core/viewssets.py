from rest_framework import viewsets
from authentication.mixins import ActionBasedPermMixin

from core.mixins import QuerysetMapperMixin, SerializerMapperMixin
from core.renderer import FormattedJSONRenderrer
from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """Custom DRF pagination class t oactivate page size query param"""
    page_size = 10
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    max_page_size = 100

class AugmentedViewSet(SerializerMapperMixin, ActionBasedPermMixin, QuerysetMapperMixin, viewsets.GenericViewSet):
    """utility viewset tha combins serializer, queryset mapping. and action-based permission mixins"""
    renderer_classes = [FormattedJSONRenderrer]
    filterset_fields = None
    pagination_class = CustomPagination