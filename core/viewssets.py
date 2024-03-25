from rest_framework import viewsets
from authentication.mixins import ActionBasedPermMixin

from core.mixins import QuerysetMapperMixin, SerializerMapperMixin
from core.renderer import FormattedJSONRenderrer
from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    page_query_param = 'page'
    max_page_size = 10

class AugmentedViewSet(SerializerMapperMixin, ActionBasedPermMixin, QuerysetMapperMixin, viewsets.GenericViewSet):
    
    renderer_classes = [FormattedJSONRenderrer]
    filterset_fields = None
    pagination_class = CustomPagination